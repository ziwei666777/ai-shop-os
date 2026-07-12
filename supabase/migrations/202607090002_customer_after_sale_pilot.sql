create type public.connector_platform as enum ('shopify', 'taobao');
create type public.connector_status as enum ('connected', 'pending', 'not_connected');
create type public.automation_decision as enum ('auto_reply', 'human_review');
create type public.message_intent as enum ('faq', 'order', 'logistics', 'refund', 'complaint', 'compensation', 'unknown');
create type public.after_sale_case_type as enum ('refund', 'return', 'logistics_issue', 'complaint', 'compensation');
create type public.after_sale_status as enum ('open', 'waiting_merchant', 'resolved');
create type public.learning_action as enum ('accepted', 'edited', 'rejected', 'manual_answered');

create table public.platform_connections (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  platform public.connector_platform not null,
  status public.connector_status not null default 'pending',
  shop_identifier text not null,
  scopes text[] not null default '{}',
  access_token_encrypted text,
  refresh_token_encrypted text,
  connected_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (company_id, platform, shop_identifier)
);

alter table public.messages
  add column if not exists platform public.connector_platform,
  add column if not exists platform_message_id text,
  add column if not exists intent public.message_intent not null default 'unknown',
  add column if not exists automation_decision public.automation_decision not null default 'human_review',
  add column if not exists ai_draft_content text,
  add column if not exists ai_sent_at timestamptz,
  add column if not exists merchant_edited boolean not null default false,
  add column if not exists final_content text;

create table public.after_sale_cases (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  platform public.connector_platform not null,
  customer_id uuid references public.customers(id) on delete set null,
  order_id uuid references public.orders(id) on delete set null,
  agent_id uuid references public.agents(id) on delete set null,
  case_type public.after_sale_case_type not null,
  status public.after_sale_status not null default 'open',
  title text not null,
  description text not null,
  risk_level text not null default 'medium',
  ai_suggestion text not null default '',
  approval_required boolean not null default true,
  merchant_decision text,
  merchant_note text,
  decided_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.learning_events (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  agent_id uuid references public.agents(id) on delete set null,
  source_type text not null,
  source_id uuid,
  action public.learning_action not null,
  original_content text not null,
  final_content text not null,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.agent_feedback_metrics (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  agent_id uuid references public.agents(id) on delete set null,
  metric_name text not null,
  metric_value numeric not null default 0,
  weight numeric(4, 3) not null default 0,
  measured_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create unique index messages_company_platform_message_idx
  on public.messages(company_id, platform, platform_message_id)
  where platform_message_id is not null;

create index platform_connections_company_idx on public.platform_connections(company_id);
create index after_sale_cases_company_status_idx on public.after_sale_cases(company_id, status);
create index after_sale_cases_company_type_idx on public.after_sale_cases(company_id, case_type);
create index learning_events_company_agent_idx on public.learning_events(company_id, agent_id);
create index agent_feedback_metrics_company_agent_idx on public.agent_feedback_metrics(company_id, agent_id);

do $$
declare
  table_name text;
begin
  foreach table_name in array array[
    'platform_connections',
    'after_sale_cases',
    'learning_events',
    'agent_feedback_metrics'
  ]
  loop
    execute format('create trigger %I_set_updated_at before update on public.%I for each row execute function public.set_updated_at()', table_name, table_name);
    execute format('alter table public.%I enable row level security', table_name);
    execute format(
      'create policy %I_company_member_select on public.%I for select using (public.is_company_member(company_id))',
      table_name,
      table_name
    );
  end loop;
end $$;
