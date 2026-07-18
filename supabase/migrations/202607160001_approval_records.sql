create table if not exists public.approval_records (
  id text primary key,
  company_id uuid not null references public.companies(id) on delete cascade,
  agent_id uuid references public.agents(id) on delete set null,
  title text not null,
  risk_level text not null check (risk_level in ('low', 'medium', 'high')),
  status text not null check (status in ('pending', 'approved', 'rejected')),
  source_type text not null,
  source_id text not null,
  reason text not null default '',
  recommended_action text not null default '',
  decision_note text,
  decided_at timestamptz,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists approval_records_company_status_created_idx
  on public.approval_records(company_id, status, created_at desc);

create index if not exists approval_records_company_source_idx
  on public.approval_records(company_id, source_type, source_id);

create index if not exists approval_records_company_risk_created_idx
  on public.approval_records(company_id, risk_level, created_at desc);

drop trigger if exists approval_records_set_updated_at on public.approval_records;
create trigger approval_records_set_updated_at
before update on public.approval_records
for each row execute function public.set_updated_at();

alter table public.approval_records enable row level security;

drop policy if exists approval_records_company_member_select on public.approval_records;
create policy approval_records_company_member_select
on public.approval_records
for select using (public.is_company_member(company_id));