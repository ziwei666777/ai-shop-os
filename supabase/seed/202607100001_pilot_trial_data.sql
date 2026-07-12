-- AI Shop OS 商家试用种子数据。
-- 只用于演示 AI客服、AI售后、Dashboard 和平台连接状态，不属于生产结构迁移。

insert into public.companies (id, name)
values ('00000000-0000-4000-8000-000000000001', 'AI Shop OS 试用商家')
on conflict (id) do update set name = excluded.name;

insert into public.agents (id, company_id, slug, name, type, status, description)
values
  (
    '00000000-0000-4000-8000-000000000101',
    '00000000-0000-4000-8000-000000000001',
    'ai-boss',
    'AI Boss',
    'boss',
    'online',
    '每天生成 CEO 汇报、识别异常、汇总审批并分配 AI 员工任务。'
  ),
  (
    '00000000-0000-4000-8000-000000000102',
    '00000000-0000-4000-8000-000000000001',
    'ai-customer',
    'AI Customer',
    'customer',
    'online',
    '负责商品咨询、订单查询、物流查询、退款说明和未知问题升级。'
  ),
  (
    '00000000-0000-4000-8000-000000000103',
    '00000000-0000-4000-8000-000000000001',
    'ai-after-sale',
    'AI After-sale',
    'after_sale',
    'online',
    '负责退款、退货、物流异常、投诉和赔偿的风险判断与审批建议。'
  )
on conflict (company_id, slug) do update
set
  name = excluded.name,
  type = excluded.type,
  status = excluded.status,
  description = excluded.description;

insert into public.agent_prompts (id, company_id, agent_id, version, content, is_active)
values
  (
    '00000000-0000-4000-8000-000000000201',
    '00000000-0000-4000-8000-000000000001',
    '00000000-0000-4000-8000-000000000101',
    1,
    '你是 AI Shop OS 的 AI Boss，只给出可追踪、可审批、可执行的经营建议。',
    true
  ),
  (
    '00000000-0000-4000-8000-000000000202',
    '00000000-0000-4000-8000-000000000001',
    '00000000-0000-4000-8000-000000000102',
    1,
    '你是 AI 客服，禁止编造答案；不确定时必须暂停并升级给老板。',
    true
  ),
  (
    '00000000-0000-4000-8000-000000000203',
    '00000000-0000-4000-8000-000000000001',
    '00000000-0000-4000-8000-000000000103',
    1,
    '你是 AI 售后，涉及退款、赔偿、投诉和金额变化时必须要求商家确认。',
    true
  )
on conflict (id) do update
set content = excluded.content, is_active = excluded.is_active;

insert into public.agent_kpis (id, company_id, agent_id, metric_name, metric_value)
values
  ('00000000-0000-4000-8000-000000000301', '00000000-0000-4000-8000-000000000001', '00000000-0000-4000-8000-000000000101', '经营建议准确率', 86),
  ('00000000-0000-4000-8000-000000000302', '00000000-0000-4000-8000-000000000001', '00000000-0000-4000-8000-000000000102', '客服采纳率', 91),
  ('00000000-0000-4000-8000-000000000303', '00000000-0000-4000-8000-000000000001', '00000000-0000-4000-8000-000000000103', '售后建议采纳率', 82)
on conflict (id) do update set metric_value = excluded.metric_value;

insert into public.customers (id, company_id, external_id, name, email, tags)
values
  ('00000000-0000-4000-8000-000000000401', '00000000-0000-4000-8000-000000000001', 'shopify-cus-1001', 'Lily Chen', 'lily@example.com', array['高意向客户']),
  ('00000000-0000-4000-8000-000000000402', '00000000-0000-4000-8000-000000000001', 'shopify-cus-1002', 'Alex Wong', 'alex@example.com', array['物流咨询']),
  ('00000000-0000-4000-8000-000000000403', '00000000-0000-4000-8000-000000000001', 'taobao-cus-1003', '王女士', null, array['售后高风险'])
on conflict (id) do update
set name = excluded.name, external_id = excluded.external_id, tags = excluded.tags;

insert into public.orders (id, company_id, customer_id, external_id, status, total_amount, paid_at)
values
  ('00000000-0000-4000-8000-000000000501', '00000000-0000-4000-8000-000000000001', '00000000-0000-4000-8000-000000000402', '#1007', '运输中，预计 2 天内送达', 389.00, now() - interval '1 day'),
  ('00000000-0000-4000-8000-000000000502', '00000000-0000-4000-8000-000000000001', '00000000-0000-4000-8000-000000000403', 'TB20260709003', '已签收', 218.00, now() - interval '3 days')
on conflict (id) do update
set status = excluded.status, total_amount = excluded.total_amount;

insert into public.conversations (id, company_id, customer_id, agent_id, channel, status)
values
  ('00000000-0000-4000-8000-000000000601', '00000000-0000-4000-8000-000000000001', '00000000-0000-4000-8000-000000000401', '00000000-0000-4000-8000-000000000102', 'shopify_inbox', 'open'),
  ('00000000-0000-4000-8000-000000000602', '00000000-0000-4000-8000-000000000001', '00000000-0000-4000-8000-000000000402', '00000000-0000-4000-8000-000000000102', 'shopify_inbox', 'open'),
  ('00000000-0000-4000-8000-000000000603', '00000000-0000-4000-8000-000000000001', '00000000-0000-4000-8000-000000000403', '00000000-0000-4000-8000-000000000102', 'taobao_message', 'open')
on conflict (id) do update set status = excluded.status;

insert into public.messages (
  id,
  company_id,
  conversation_id,
  sender_type,
  content,
  confidence,
  requires_human_review,
  platform,
  platform_message_id,
  intent,
  automation_decision,
  ai_draft_content,
  merchant_edited,
  final_content
)
values
  (
    '00000000-0000-4000-8000-000000000701',
    '00000000-0000-4000-8000-000000000001',
    '00000000-0000-4000-8000-000000000601',
    'customer',
    '这件衬衫还有 M 码吗？今天下单什么时候发货？',
    0.9200,
    false,
    'shopify',
    'shopify-msg-1001',
    'faq',
    'auto_reply',
    '您好，这款商品当前可以正常咨询和下单，M 码库存请以页面展示为准；今天下单预计 24 小时内发货。',
    false,
    null
  ),
  (
    '00000000-0000-4000-8000-000000000702',
    '00000000-0000-4000-8000-000000000001',
    '00000000-0000-4000-8000-000000000602',
    'customer',
    '订单 #1007 到哪里了？',
    0.8800,
    false,
    'shopify',
    'shopify-msg-1002',
    'logistics',
    'auto_reply',
    '您好，您的订单 #1007 当前状态是：运输中，预计 2 天内送达。我会继续帮您关注物流更新。',
    false,
    null
  ),
  (
    '00000000-0000-4000-8000-000000000703',
    '00000000-0000-4000-8000-000000000001',
    '00000000-0000-4000-8000-000000000603',
    'customer',
    '收到货有瑕疵，可以赔偿吗？',
    0.6700,
    true,
    'taobao',
    'taobao-msg-1003',
    'compensation',
    'human_review',
    '这个问题涉及赔偿金额，需要商家确认后再回复。',
    false,
    null
  )
on conflict (id) do update
set
  content = excluded.content,
  confidence = excluded.confidence,
  requires_human_review = excluded.requires_human_review,
  intent = excluded.intent,
  automation_decision = excluded.automation_decision,
  ai_draft_content = excluded.ai_draft_content;

insert into public.platform_connections (id, company_id, platform, status, shop_identifier, scopes, connected_at)
values
  (
    '00000000-0000-4000-8000-000000000801',
    '00000000-0000-4000-8000-000000000001',
    'shopify',
    'pending',
    'demo-shop.myshopify.com',
    array['read_orders', 'read_products', 'read_customers'],
    null
  ),
  (
    '00000000-0000-4000-8000-000000000802',
    '00000000-0000-4000-8000-000000000001',
    'taobao',
    'pending',
    'taobao-open-platform',
    array['订单查询', '物流查询', '消息接入'],
    null
  )
on conflict (company_id, platform, shop_identifier) do update
set status = excluded.status, scopes = excluded.scopes;

insert into public.after_sale_cases (
  id,
  company_id,
  platform,
  customer_id,
  order_id,
  agent_id,
  case_type,
  status,
  title,
  description,
  risk_level,
  ai_suggestion,
  approval_required
)
values
  (
    '00000000-0000-4000-8000-000000000901',
    '00000000-0000-4000-8000-000000000001',
    'shopify',
    '00000000-0000-4000-8000-000000000402',
    '00000000-0000-4000-8000-000000000501',
    '00000000-0000-4000-8000-000000000103',
    'refund',
    'waiting_merchant',
    '客户申请退款',
    '客户表示物流超过预期，希望退款。',
    'medium',
    '先核查物流轨迹，如果 48 小时内无更新，再建议部分补偿或退款审批。',
    true
  ),
  (
    '00000000-0000-4000-8000-000000000902',
    '00000000-0000-4000-8000-000000000001',
    'taobao',
    '00000000-0000-4000-8000-000000000403',
    '00000000-0000-4000-8000-000000000502',
    '00000000-0000-4000-8000-000000000103',
    'complaint',
    'waiting_merchant',
    '商品瑕疵投诉',
    '客户反馈商品有瑕疵并提出赔偿。',
    'high',
    '需要人工查看图片证据；未确认前不得承诺赔偿金额。',
    true
  )
on conflict (id) do update
set
  status = excluded.status,
  risk_level = excluded.risk_level,
  ai_suggestion = excluded.ai_suggestion,
  approval_required = excluded.approval_required;

insert into public.agent_feedback_metrics (id, company_id, agent_id, metric_name, metric_value, weight)
values
  ('00000000-0000-4000-8000-000000001001', '00000000-0000-4000-8000-000000000001', '00000000-0000-4000-8000-000000000102', '客服问答修正样本', 60, 0.600),
  ('00000000-0000-4000-8000-000000001002', '00000000-0000-4000-8000-000000000001', '00000000-0000-4000-8000-000000000103', '售后决策样本', 30, 0.300),
  ('00000000-0000-4000-8000-000000001003', '00000000-0000-4000-8000-000000000001', '00000000-0000-4000-8000-000000000102', '采纳率与接管率', 10, 0.100)
on conflict (id) do update
set metric_value = excluded.metric_value, weight = excluded.weight;

insert into public.daily_business_snapshots (
  id,
  company_id,
  snapshot_date,
  sales_amount,
  profit_amount,
  order_count,
  refund_count,
  pending_approval_count,
  inventory_risk_count,
  ad_spend
)
values (
  '00000000-0000-4000-8000-000000001101',
  '00000000-0000-4000-8000-000000000001',
  current_date,
  12860.00,
  3420.00,
  48,
  7,
  3,
  5,
  1680.00
)
on conflict (id) do update
set
  snapshot_date = excluded.snapshot_date,
  sales_amount = excluded.sales_amount,
  profit_amount = excluded.profit_amount,
  order_count = excluded.order_count,
  refund_count = excluded.refund_count,
  pending_approval_count = excluded.pending_approval_count,
  inventory_risk_count = excluded.inventory_risk_count,
  ad_spend = excluded.ad_spend;
