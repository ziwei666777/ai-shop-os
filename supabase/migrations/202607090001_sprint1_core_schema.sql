create extension if not exists "pgcrypto";
create extension if not exists "vector";

create type public.agent_type as enum (
  'boss',
  'customer',
  'operator',
  'after_sale',
  'purchase',
  'logistics',
  'finance',
  'analyst'
);

create type public.agent_status as enum ('online', 'paused', 'offline');
create type public.memory_type as enum ('conversation', 'customer', 'business', 'company');
create type public.approval_status as enum ('pending', 'approved', 'rejected', 'cancelled');
create type public.workflow_status as enum ('draft', 'active', 'paused', 'archived');

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create table public.companies (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  owner_user_id uuid,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.users (
  id uuid primary key references auth.users(id) on delete cascade,
  company_id uuid references public.companies(id) on delete set null,
  email text not null unique,
  display_name text not null,
  avatar_url text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.companies
  add constraint companies_owner_user_id_fkey
  foreign key (owner_user_id) references public.users(id) on delete set null;

create table public.company_members (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  user_id uuid not null references public.users(id) on delete cascade,
  role text not null default 'owner',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (company_id, user_id)
);

create table public.agents (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  slug text not null,
  name text not null,
  type public.agent_type not null,
  status public.agent_status not null default 'paused',
  description text not null default '',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (company_id, slug)
);

create table public.agent_prompts (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  agent_id uuid not null references public.agents(id) on delete cascade,
  version integer not null default 1,
  content text not null,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.agent_tools (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  agent_id uuid not null references public.agents(id) on delete cascade,
  name text not null,
  mcp_server text not null,
  permission_scope text not null default 'read',
  is_enabled boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.agent_kpis (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  agent_id uuid not null references public.agents(id) on delete cascade,
  metric_name text not null,
  metric_value numeric not null default 0,
  measured_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.customers (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  external_id text,
  name text not null,
  phone text,
  email text,
  tags text[] not null default '{}',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.products (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  external_id text,
  title text not null,
  sku text,
  price numeric(12, 2) not null default 0,
  inventory_count integer not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.orders (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  customer_id uuid references public.customers(id) on delete set null,
  external_id text,
  status text not null default 'pending',
  total_amount numeric(12, 2) not null default 0,
  paid_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.conversations (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  customer_id uuid references public.customers(id) on delete set null,
  agent_id uuid references public.agents(id) on delete set null,
  channel text not null default 'manual',
  status text not null default 'open',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.messages (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  conversation_id uuid not null references public.conversations(id) on delete cascade,
  sender_type text not null,
  sender_id uuid,
  content text not null,
  confidence numeric(5, 4),
  requires_human_review boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.knowledge_sources (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  title text not null,
  source_type text not null,
  uri text,
  status text not null default 'pending_embedding',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.knowledge_chunks (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  knowledge_source_id uuid not null references public.knowledge_sources(id) on delete cascade,
  content text not null,
  embedding vector(1536),
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.memories (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  agent_id uuid references public.agents(id) on delete set null,
  customer_id uuid references public.customers(id) on delete cascade,
  conversation_id uuid references public.conversations(id) on delete cascade,
  memory_type public.memory_type not null,
  title text not null,
  content text not null,
  confidence numeric(5, 4) not null default 1,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.workflows (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  agent_id uuid references public.agents(id) on delete set null,
  name text not null,
  status public.workflow_status not null default 'draft',
  definition jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.workflow_runs (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  workflow_id uuid not null references public.workflows(id) on delete cascade,
  agent_id uuid references public.agents(id) on delete set null,
  status text not null default 'queued',
  input jsonb not null default '{}'::jsonb,
  output jsonb not null default '{}'::jsonb,
  started_at timestamptz,
  finished_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.workflow_steps (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  workflow_run_id uuid not null references public.workflow_runs(id) on delete cascade,
  step_key text not null,
  status text not null default 'queued',
  input jsonb not null default '{}'::jsonb,
  output jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.approvals (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  agent_id uuid references public.agents(id) on delete set null,
  workflow_run_id uuid references public.workflow_runs(id) on delete set null,
  title text not null,
  reason text not null,
  risk_level text not null default 'medium',
  status public.approval_status not null default 'pending',
  requested_by text not null default 'agent',
  decided_by uuid references public.users(id) on delete set null,
  decided_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.agent_logs (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  agent_id uuid references public.agents(id) on delete set null,
  workflow_run_id uuid references public.workflow_runs(id) on delete set null,
  level text not null default 'info',
  message text not null,
  context jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.audit_logs (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  actor_user_id uuid references public.users(id) on delete set null,
  action text not null,
  target_type text not null,
  target_id uuid,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.daily_business_snapshots (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  snapshot_date date not null,
  sales_amount numeric(12, 2) not null default 0,
  profit_amount numeric(12, 2) not null default 0,
  order_count integer not null default 0,
  refund_count integer not null default 0,
  pending_approval_count integer not null default 0,
  inventory_risk_count integer not null default 0,
  ad_spend numeric(12, 2) not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (company_id, snapshot_date)
);

create index users_company_id_idx on public.users(company_id);
create index company_members_company_id_idx on public.company_members(company_id);
create index agents_company_id_idx on public.agents(company_id);
create index agents_type_idx on public.agents(type);
create index agent_prompts_agent_id_idx on public.agent_prompts(agent_id);
create index agent_tools_agent_id_idx on public.agent_tools(agent_id);
create index agent_kpis_agent_id_idx on public.agent_kpis(agent_id);
create index customers_company_id_idx on public.customers(company_id);
create index products_company_id_idx on public.products(company_id);
create index orders_company_id_idx on public.orders(company_id);
create index conversations_company_id_idx on public.conversations(company_id);
create index messages_conversation_id_idx on public.messages(conversation_id);
create index knowledge_chunks_source_id_idx on public.knowledge_chunks(knowledge_source_id);
create index memories_company_type_idx on public.memories(company_id, memory_type);
create index workflows_company_id_idx on public.workflows(company_id);
create index workflow_runs_workflow_id_idx on public.workflow_runs(workflow_id);
create index workflow_steps_run_id_idx on public.workflow_steps(workflow_run_id);
create index approvals_company_status_idx on public.approvals(company_id, status);
create index agent_logs_agent_id_idx on public.agent_logs(agent_id);
create index audit_logs_company_id_idx on public.audit_logs(company_id);
create index daily_snapshots_company_date_idx on public.daily_business_snapshots(company_id, snapshot_date);

create index knowledge_chunks_embedding_idx
  on public.knowledge_chunks
  using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);

do $$
declare
  table_name text;
begin
  foreach table_name in array array[
    'companies',
    'users',
    'company_members',
    'agents',
    'agent_prompts',
    'agent_tools',
    'agent_kpis',
    'customers',
    'products',
    'orders',
    'conversations',
    'messages',
    'knowledge_sources',
    'knowledge_chunks',
    'memories',
    'workflows',
    'workflow_runs',
    'workflow_steps',
    'approvals',
    'agent_logs',
    'audit_logs',
    'daily_business_snapshots'
  ]
  loop
    execute format('create trigger %I_set_updated_at before update on public.%I for each row execute function public.set_updated_at()', table_name, table_name);
    execute format('alter table public.%I enable row level security', table_name);
  end loop;
end $$;

-- RLS 策略先以组织成员隔离为核心，后续接入 Supabase Auth 后可继续细分读写权限。
create or replace function public.is_company_member(target_company_id uuid)
returns boolean
language sql
security definer
set search_path = public
as $$
  select exists (
    select 1
    from public.company_members cm
    where cm.company_id = target_company_id
      and cm.user_id = auth.uid()
  );
$$;

create policy company_member_select_companies on public.companies
for select using (public.is_company_member(id));

do $$
declare
  table_name text;
begin
  foreach table_name in array array[
    'users',
    'company_members',
    'agents',
    'agent_prompts',
    'agent_tools',
    'agent_kpis',
    'customers',
    'products',
    'orders',
    'conversations',
    'messages',
    'knowledge_sources',
    'knowledge_chunks',
    'memories',
    'workflows',
    'workflow_runs',
    'workflow_steps',
    'approvals',
    'agent_logs',
    'audit_logs',
    'daily_business_snapshots'
  ]
  loop
    execute format(
      'create policy %I_company_member_select on public.%I for select using (public.is_company_member(company_id))',
      table_name,
      table_name
    );
  end loop;
end $$;
