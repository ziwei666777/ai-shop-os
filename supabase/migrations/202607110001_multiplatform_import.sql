-- 国内三平台数据导入：只保存业务所需字段，不保存完整平台响应或多余敏感信息。
alter type public.connector_platform add value if not exists 'douyin';
alter type public.connector_platform add value if not exists 'xianyu';

alter table public.platform_connections
  add column if not exists authorization_mode text not null default 'service_provider',
  add column if not exists token_expires_at timestamptz,
  add column if not exists refresh_token_expires_at timestamptz,
  add column if not exists last_synced_at timestamptz,
  add column if not exists last_error text;

alter table public.products
  add column if not exists platform public.connector_platform,
  add column if not exists platform_connection_id uuid references public.platform_connections(id) on delete set null,
  add column if not exists external_updated_at timestamptz,
  add column if not exists source_metadata jsonb not null default '{}'::jsonb;

alter table public.orders
  add column if not exists platform public.connector_platform,
  add column if not exists platform_connection_id uuid references public.platform_connections(id) on delete set null,
  add column if not exists external_updated_at timestamptz,
  add column if not exists source_metadata jsonb not null default '{}'::jsonb;

alter table public.customers
  add column if not exists platform public.connector_platform,
  add column if not exists platform_connection_id uuid references public.platform_connections(id) on delete set null,
  add column if not exists external_updated_at timestamptz,
  add column if not exists source_metadata jsonb not null default '{}'::jsonb;

alter table public.after_sale_cases
  add column if not exists external_id text,
  add column if not exists platform_connection_id uuid references public.platform_connections(id) on delete set null,
  add column if not exists external_updated_at timestamptz,
  add column if not exists source_metadata jsonb not null default '{}'::jsonb;

create table public.order_items (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  order_id uuid not null references public.orders(id) on delete cascade,
  product_id uuid references public.products(id) on delete set null,
  platform_connection_id uuid references public.platform_connections(id) on delete set null,
  external_id text not null,
  sku text,
  title text not null,
  quantity integer not null default 1 check (quantity > 0),
  unit_price numeric(12, 2) not null default 0 check (unit_price >= 0),
  source_metadata jsonb not null default '{}'::jsonb,
  external_updated_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.shipments (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  order_id uuid references public.orders(id) on delete set null,
  platform_connection_id uuid references public.platform_connections(id) on delete set null,
  external_id text not null,
  carrier_name text,
  tracking_number text,
  status text not null default 'unknown',
  shipped_at timestamptz,
  delivered_at timestamptz,
  source_metadata jsonb not null default '{}'::jsonb,
  external_updated_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.import_jobs (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  platform_connection_id uuid references public.platform_connections(id) on delete set null,
  platform public.connector_platform not null,
  import_mode text not null check (import_mode in ('api_sync', 'file')),
  data_type text not null check (data_type in ('products', 'orders', 'order_items', 'customers', 'shipments', 'after_sales')),
  status text not null default 'queued' check (status in ('queued', 'running', 'partial_success', 'succeeded', 'failed')),
  progress integer not null default 0 check (progress between 0 and 100),
  total_count integer not null default 0,
  success_count integer not null default 0,
  failure_count integer not null default 0,
  cursor jsonb not null default '{}'::jsonb,
  field_mapping jsonb not null default '{}'::jsonb,
  error_summary text,
  file_name text,
  file_sha256 text,
  started_at timestamptz,
  finished_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- 旧数据的连接字段允许为空；只有已接入平台的数据参与新唯一约束。
create unique index if not exists products_company_connection_external_idx
  on public.products(company_id, platform_connection_id, external_id)
  where platform_connection_id is not null and external_id is not null;
create unique index if not exists orders_company_connection_external_idx
  on public.orders(company_id, platform_connection_id, external_id)
  where platform_connection_id is not null and external_id is not null;
create unique index if not exists customers_company_connection_external_idx
  on public.customers(company_id, platform_connection_id, external_id)
  where platform_connection_id is not null and external_id is not null;
create unique index if not exists after_sales_company_connection_external_idx
  on public.after_sale_cases(company_id, platform_connection_id, external_id)
  where platform_connection_id is not null and external_id is not null;
create unique index order_items_company_connection_external_idx
  on public.order_items(company_id, platform_connection_id, external_id);
create unique index shipments_company_connection_external_idx
  on public.shipments(company_id, platform_connection_id, external_id);

create index products_company_platform_idx on public.products(company_id, platform);
create index orders_company_platform_status_idx on public.orders(company_id, platform, status);
create index customers_company_platform_idx on public.customers(company_id, platform);
create index order_items_company_order_idx on public.order_items(company_id, order_id);
create index shipments_company_status_idx on public.shipments(company_id, status);
create index import_jobs_company_created_idx on public.import_jobs(company_id, created_at desc);
create index import_jobs_company_status_idx on public.import_jobs(company_id, status);

do $$
declare
  table_name text;
begin
  foreach table_name in array array['order_items', 'shipments', 'import_jobs']
  loop
    execute format(
      'create trigger %I_set_updated_at before update on public.%I for each row execute function public.set_updated_at()',
      table_name,
      table_name
    );
    execute format('alter table public.%I enable row level security', table_name);
    execute format(
      'create policy %I_company_member_select on public.%I for select using (public.is_company_member(company_id))',
      table_name,
      table_name
    );
  end loop;
end $$;

