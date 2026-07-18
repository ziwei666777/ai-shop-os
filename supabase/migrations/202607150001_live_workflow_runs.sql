create table if not exists public.live_workflow_runs (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  platform_connection_id uuid references public.platform_connections(id) on delete set null,
  agent_id uuid references public.agents(id) on delete set null,
  workflow_name text not null,
  workflow_stage text not null check (workflow_stage in ('pre_live', 'during_live', 'post_live')),
  status text not null check (status in ('done', 'warning', 'blocked', 'pending', 'failed', 'needs_human')),
  input_snapshot jsonb not null default '{}'::jsonb,
  alerts jsonb not null default '[]'::jsonb,
  recommended_actions jsonb not null default '[]'::jsonb,
  approval_required boolean not null default false,
  proof text not null default '',
  human_action text,
  human_feedback text,
  saved_minutes integer not null default 0 check (saved_minutes >= 0),
  saved_cost_yuan numeric(12, 2) not null default 0 check (saved_cost_yuan >= 0),
  risk_score integer not null default 0 check (risk_score >= 0 and risk_score <= 100),
  confidence numeric(5, 4) check (confidence is null or (confidence >= 0 and confidence <= 1)),
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists live_workflow_runs_company_created_idx
  on public.live_workflow_runs(company_id, created_at desc);

create index if not exists live_workflow_runs_company_stage_created_idx
  on public.live_workflow_runs(company_id, workflow_stage, created_at desc);

create index if not exists live_workflow_runs_company_status_created_idx
  on public.live_workflow_runs(company_id, status, created_at desc);

create index if not exists live_workflow_runs_connection_created_idx
  on public.live_workflow_runs(platform_connection_id, created_at desc)
  where platform_connection_id is not null;

drop trigger if exists live_workflow_runs_set_updated_at on public.live_workflow_runs;
create trigger live_workflow_runs_set_updated_at
before update on public.live_workflow_runs
for each row execute function public.set_updated_at();

alter table public.live_workflow_runs enable row level security;

drop policy if exists live_workflow_runs_company_member_select on public.live_workflow_runs;
create policy live_workflow_runs_company_member_select
on public.live_workflow_runs
for select using (public.is_company_member(company_id));
