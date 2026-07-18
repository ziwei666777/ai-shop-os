create table if not exists public.after_sale_decision_outcomes (
  id text primary key,
  company_id uuid not null references public.companies(id) on delete cascade,
  approval_id text not null,
  approval_status text not null check (approval_status in ('approved', 'rejected')),
  action text not null check (action in ('refund', 'replacement', 'compensation', 'reject')),
  source_workflow_id text not null,
  after_sale_cost_yuan integer not null default 0 check (after_sale_cost_yuan >= 0),
  saved_minutes integer not null default 0 check (saved_minutes >= 0),
  saved_yuan integer not null default 0 check (saved_yuan >= 0),
  warehouse_notification_id text,
  customer_reply text not null default '',
  proof text not null default '',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.warehouse_notifications (
  id text primary key,
  company_id uuid not null references public.companies(id) on delete cascade,
  source_outcome_id text not null references public.after_sale_decision_outcomes(id) on delete cascade,
  source_workflow_id text not null,
  action text not null check (action in ('replacement')),
  status text not null default 'queued' check (status in ('queued', 'sent', 'failed', 'cancelled')),
  external_reference text,
  proof text not null default '',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists after_sale_decision_outcomes_company_created_idx
  on public.after_sale_decision_outcomes(company_id, created_at desc);

create index if not exists after_sale_decision_outcomes_company_approval_idx
  on public.after_sale_decision_outcomes(company_id, approval_id);

create index if not exists after_sale_decision_outcomes_company_workflow_idx
  on public.after_sale_decision_outcomes(company_id, source_workflow_id);

create index if not exists warehouse_notifications_company_status_created_idx
  on public.warehouse_notifications(company_id, status, created_at desc);

create index if not exists warehouse_notifications_company_workflow_idx
  on public.warehouse_notifications(company_id, source_workflow_id);

drop trigger if exists after_sale_decision_outcomes_set_updated_at on public.after_sale_decision_outcomes;
create trigger after_sale_decision_outcomes_set_updated_at
before update on public.after_sale_decision_outcomes
for each row execute function public.set_updated_at();

drop trigger if exists warehouse_notifications_set_updated_at on public.warehouse_notifications;
create trigger warehouse_notifications_set_updated_at
before update on public.warehouse_notifications
for each row execute function public.set_updated_at();

alter table public.after_sale_decision_outcomes enable row level security;
alter table public.warehouse_notifications enable row level security;

drop policy if exists after_sale_decision_outcomes_company_member_select on public.after_sale_decision_outcomes;
create policy after_sale_decision_outcomes_company_member_select
on public.after_sale_decision_outcomes
for select using (public.is_company_member(company_id));

drop policy if exists warehouse_notifications_company_member_select on public.warehouse_notifications;
create policy warehouse_notifications_company_member_select
on public.warehouse_notifications
for select using (public.is_company_member(company_id));