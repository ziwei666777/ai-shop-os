create table if not exists public.live_metric_snapshots (
  id text primary key,
  company_id uuid not null references public.companies(id) on delete cascade,
  platform text not null check (platform in ('taobao', 'douyin')),
  stream_external_id text not null,
  observed_at timestamptz not null,
  online_users integer not null check (online_users >= 0),
  conversion_rate numeric(8, 6) not null check (conversion_rate >= 0 and conversion_rate <= 1),
  retention_rate numeric(8, 6) not null check (retention_rate >= 0 and retention_rate <= 1),
  comment_count integer not null check (comment_count >= 0),
  like_count integer not null check (like_count >= 0),
  product_click_rate numeric(8, 6) not null check (product_click_rate >= 0 and product_click_rate <= 1),
  inventory_delta integer not null,
  abnormal_order_count integer not null check (abnormal_order_count >= 0),
  source_reference text not null default '',
  source_payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique (company_id, platform, stream_external_id, observed_at)
);

create index if not exists live_metric_snapshots_company_observed_idx
  on public.live_metric_snapshots(company_id, observed_at desc);

alter table public.live_metric_snapshots enable row level security;

drop policy if exists live_metric_snapshots_company_member_select on public.live_metric_snapshots;
create policy live_metric_snapshots_company_member_select
on public.live_metric_snapshots
for select using (public.is_company_member(company_id));
