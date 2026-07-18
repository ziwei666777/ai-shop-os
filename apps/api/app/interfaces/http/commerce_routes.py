import json
from urllib.parse import unquote

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request

from apps.api.app.infrastructure.commerce_catalog import list_catalog
from apps.api.app.infrastructure.commerce_dataset_readiness import get_commerce_dataset_readiness
from apps.api.app.infrastructure.import_file_parser import ImportFileError, parse_import_preview
from apps.api.app.infrastructure.import_jobs import (
    create_file_import_job,
    create_sync_jobs,
    get_import_job,
    list_import_jobs,
)
from apps.api.app.infrastructure.oauth_connectors import complete_platform_oauth, start_platform_oauth
from apps.api.app.infrastructure.platform_security import IntegrationUnavailableError
from apps.api.app.interfaces.http.auth import CompanyContext, require_company_context
from apps.api.app.interfaces.http.commerce_schemas import (
    CatalogPageResponse,
    CommerceDatasetReadinessResponse,
    DataType,
    ImportJobResponse,
    ImportPreviewResponse,
    ImportSyncRequest,
    OAuthStartResponse,
    Platform,
)


router = APIRouter(prefix="/v1", tags=["国内平台数据导入"])


@router.post("/connectors/taobao/oauth/start", response_model=OAuthStartResponse)
async def taobao_oauth_start(context: CompanyContext = Depends(require_company_context)) -> OAuthStartResponse:
    return _start_oauth("taobao", context)


@router.get("/connectors/taobao/oauth/callback")
async def taobao_oauth_callback(code: str, state: str) -> dict[str, str]:
    return await _complete_oauth("taobao", code, state)


@router.post("/connectors/douyin/oauth/start", response_model=OAuthStartResponse)
async def douyin_oauth_start(context: CompanyContext = Depends(require_company_context)) -> OAuthStartResponse:
    return _start_oauth("douyin", context)


@router.get("/connectors/douyin/oauth/callback")
async def douyin_oauth_callback(code: str, state: str) -> dict[str, str]:
    return await _complete_oauth("douyin", code, state)


@router.post("/imports/preview", response_model=ImportPreviewResponse)
async def preview_import_file(
    request: Request,
    file_name: str = Query(min_length=1),
    platform: Platform = Query(),
    data_type: DataType = Query(),
    _: CompanyContext = Depends(require_company_context),
) -> ImportPreviewResponse:
    del platform
    content = await request.body()
    try:
        preview = parse_import_preview(file_name, content, data_type)
    except ImportFileError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return ImportPreviewResponse.model_validate(preview, from_attributes=True)


@router.post("/imports/files", response_model=ImportJobResponse, status_code=202)
async def submit_import_file(
    request: Request,
    file_name: str = Query(min_length=1),
    platform: Platform = Query(),
    data_type: DataType = Query(),
    shop_name: str = Query(min_length=1),
    platform_connection_id: str | None = Query(default=None),
    x_field_mapping: str = Header(default="{}", alias="X-Field-Mapping"),
    context: CompanyContext = Depends(require_company_context),
) -> ImportJobResponse:
    content = await request.body()
    try:
        parse_import_preview(file_name, content, data_type)
        mapping = json.loads(unquote(x_field_mapping))
        if not isinstance(mapping, dict) or not all(isinstance(key, str) and isinstance(value, str) for key, value in mapping.items()):
            raise ValueError("字段映射格式错误。")
        job = create_file_import_job(
            context.company_id, platform, shop_name, data_type, file_name, content, mapping, platform_connection_id
        )
    except (ImportFileError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except IntegrationUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return ImportJobResponse.model_validate(job)


@router.post("/imports/sync", response_model=list[ImportJobResponse], status_code=202)
async def start_incremental_sync(
    payload: ImportSyncRequest,
    context: CompanyContext = Depends(require_company_context),
) -> list[ImportJobResponse]:
    try:
        jobs = create_sync_jobs(
            context.company_id, payload.platform, payload.platform_connection_id, list(dict.fromkeys(payload.data_types))
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except IntegrationUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return [ImportJobResponse.model_validate(job) for job in jobs]


@router.get("/imports", response_model=list[ImportJobResponse])
async def import_jobs(context: CompanyContext = Depends(require_company_context)) -> list[ImportJobResponse]:
    return [ImportJobResponse.model_validate(job) for job in list_import_jobs(context.company_id)]


@router.get("/imports/{job_id}", response_model=ImportJobResponse)
async def import_job(job_id: str, context: CompanyContext = Depends(require_company_context)) -> ImportJobResponse:
    job = get_import_job(context.company_id, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="导入任务不存在。")
    return ImportJobResponse.model_validate(job)


@router.get("/commerce-dataset/readiness", response_model=CommerceDatasetReadinessResponse)
async def commerce_dataset_readiness(context: CompanyContext = Depends(require_company_context)) -> CommerceDatasetReadinessResponse:
    summary = get_commerce_dataset_readiness(context.company_id)
    return CommerceDatasetReadinessResponse.model_validate(summary, from_attributes=True)


@router.get("/orders", response_model=CatalogPageResponse)
async def orders(
    platform: Platform | None = None,
    status: str | None = None,
    keyword: str | None = None,
    start_at: str | None = None,
    end_at: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    context: CompanyContext = Depends(require_company_context),
) -> CatalogPageResponse:
    del start_at, end_at
    return _catalog_page("orders", context, platform, status, keyword, page, page_size)


@router.get("/products", response_model=CatalogPageResponse)
async def products(
    platform: Platform | None = None,
    status: str | None = None,
    keyword: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    context: CompanyContext = Depends(require_company_context),
) -> CatalogPageResponse:
    return _catalog_page("products", context, platform, status, keyword, page, page_size)


@router.get("/customers", response_model=CatalogPageResponse)
async def customers(
    platform: Platform | None = None,
    keyword: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    context: CompanyContext = Depends(require_company_context),
) -> CatalogPageResponse:
    return _catalog_page("customers", context, platform, None, keyword, page, page_size)


@router.get("/shipments", response_model=CatalogPageResponse)
async def shipments(
    platform: Platform | None = None,
    status: str | None = None,
    keyword: str | None = None,
    start_at: str | None = None,
    end_at: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    context: CompanyContext = Depends(require_company_context),
) -> CatalogPageResponse:
    del start_at, end_at
    return _catalog_page("shipments", context, platform, status, keyword, page, page_size)


def _start_oauth(platform: Platform, context: CompanyContext) -> OAuthStartResponse:
    try:
        url = start_platform_oauth(platform, context.user_id, context.company_id)
    except IntegrationUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return OAuthStartResponse(authorization_url=url, platform=platform)


async def _complete_oauth(platform: Platform, code: str, state: str) -> dict[str, str]:
    try:
        _, result = await complete_platform_oauth(platform, code, state)
    except IntegrationUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except httpx.HTTPError as error:
        raise HTTPException(status_code=502, detail="平台授权服务暂时不可用，请稍后重试。") from error
    return {"status": "connected", "platform": platform, "shop": result.shop_name}


def _catalog_page(
    kind: str,
    context: CompanyContext,
    platform: Platform | None,
    status: str | None,
    keyword: str | None,
    page: int,
    page_size: int,
) -> CatalogPageResponse:
    items, total = list_catalog(kind, context.company_id, platform, status, keyword, page, page_size)
    return CatalogPageResponse(items=items, total=total, page=page, page_size=page_size)
