create table if not exists public.ceo_daily_report_snapshots (
  id text primary key,
  company_id uuid not null references public.companies(id) on delete cascade,
  snapshot_date date not null,
  report jsonb not null default '{}'::jsonb,
  data_status text not null check (data_status in ('demo_estimate', 'real_workflow_logs')),
  saved_money_today_yuan integer not null default 0 check (saved_money_today_yuan >= 0),
  projected_monthly_saving_yuan integer not null default 0 check (projected_monthly_saving_yuan >= 0),
  annual_roi_percent integer not null default 0,
  proof_points jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (company_id, snapshot_date)
);

create index if not exists ceo_daily_report_snapshots_company_date_idx
  on public.ceo_daily_report_snapshots(company_id, snapshot_date desc);

drop trigger if exists ceo_daily_report_snapshots_set_updated_at on public.ceo_daily_report_snapshots;
create trigger ceo_daily_report_snapshots_set_updated_at
before update on public.ceo_daily_report_snapshots
for each row execute function public.set_updated_at();

alter table public.ceo_daily_report_snapshots enable row level security;

drop policy if exists ceo_daily_report_snapshots_company_member_select on public.ceo_daily_report_snapshots;
create policy ceo_daily_report_snapshots_company_member_select
on public.ceo_daily_report_snapshots
for select using (public.is_company_member(company_id));
