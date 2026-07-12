import "server-only";

import { createServerSupabaseClient } from "./supabase-server";
import { fallbackCustomers, fallbackOrders, fallbackProducts } from "./fallback-data";
import type { CatalogPage, CustomerItem, ImportJob, OrderItem, ProductItem } from "./types";


const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const COMPANY_ID = process.env.NEXT_PUBLIC_DEFAULT_COMPANY_ID ?? "00000000-0000-0000-0000-000000000001";

async function serverRequest<T>(path: string, fallback: T): Promise<T> {
  try {
    const { data } = await (await createServerSupabaseClient()).auth.getSession();
    const response = await fetch(`${API_BASE_URL}${path}`, {
      cache: "no-store",
      headers: {
        accept: "application/json",
        "X-Company-ID": COMPANY_ID,
        ...(data.session ? { Authorization: `Bearer ${data.session.access_token}` } : {})
      }
    });
    return response.ok ? ((await response.json()) as T) : fallback;
  } catch {
    return fallback;
  }
}

export async function listProductsForPage(): Promise<ProductItem[]> {
  const fallback = { items: fallbackProducts, total: fallbackProducts.length, page: 1, page_size: 20 };
  return (await serverRequest<CatalogPage<ProductItem>>("/v1/products", fallback)).items;
}

export async function listOrdersForPage(): Promise<OrderItem[]> {
  const fallback = { items: fallbackOrders, total: fallbackOrders.length, page: 1, page_size: 20 };
  return (await serverRequest<CatalogPage<OrderItem>>("/v1/orders", fallback)).items;
}

export async function listCustomersForPage(): Promise<CustomerItem[]> {
  const fallback = { items: fallbackCustomers, total: fallbackCustomers.length, page: 1, page_size: 20 };
  return (await serverRequest<CatalogPage<CustomerItem>>("/v1/customers", fallback)).items;
}

export async function listImportJobsForPage(): Promise<ImportJob[]> {
  return serverRequest<ImportJob[]>("/v1/imports", []);
}
