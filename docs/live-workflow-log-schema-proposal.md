# 鐩存挱 Workflow 鏃ュ織琛ㄨ璁℃柟妗堬紙寰呯‘璁わ紝涓嶆墽琛岋級

## 涓轰粈涔堥渶瑕佽繖寮犺〃

褰撳墠鐩存挱 Workflow 鏃ュ織鍏堝瓨鍦ㄥ悗绔唴瀛橀噷锛岄€傚悎鏈湴楠岃瘉锛屼絾涓嶉€傚悎鐪熷疄鍟嗗闀挎湡浣跨敤銆傜湡瀹炲晢瀹朵娇鐢ㄦ椂锛岀郴缁熷繀椤绘案涔呰褰曪細

1. AI 鍋氫簡浠€涔堝伐浣溿€?2. 鍙戠幇浜嗕粈涔堥闄┿€?3. 寤鸿浜嗕粈涔堝姩浣溿€?4. 鍟嗗鏄惁閲囩撼銆?5. 鏈€鍚庤妭鐪佷簡澶氬皯鏃堕棿鍜屽灏戦挶銆?
杩欏紶琛ㄦ槸 Savings Engine 鍜?ROI Engine 鐨勮瘉鎹潵婧愩€?
## 鏇夸唬宀椾綅

鐩存挱杩愯惀鍔╃悊銆?
## 涓€澶╄妭鐪佹椂闂?
姣忎釜搴楅摵姣忓ぉ棰勮鑺傜渷 80 鍒?190 鍒嗛挓锛屼富瑕佹潵鑷紑鎾鏌ャ€佺洿鎾洴鐩樸€佷笅鎾鐩樸€?
## 涓€涓湀鑺傜渷浜哄伐

鎸?26 澶╄绠楋紝姣忔湀棰勮鑺傜渷 35 鍒?82 灏忔椂銆傛寜娣卞湷鐩存挱杩愯惀鍔╃悊缁煎悎鎴愭湰姣忓皬鏃?35 鍏冧及绠楋紝姣忔湀绾﹁妭鐪?1225 鍒?2870 鍏冦€傚涓洿鎾棿鍙犲姞鍚庝环鍊兼洿楂樸€?
## 鑰佹澘涓轰粈涔堟効鎰忎粯閽?
鑰佹澘涓嶆槸涓轰竴涓〉闈粯閽憋紝鑰屾槸涓衡€滄瘡澶╁皯闆囦竴涓汉鐩洿鎾棿锛屽苟涓旇繕鑳界湅鍒拌妭鐪侀噾棰濊瘉鎹€濅粯閽便€?
## 寤鸿鏂板琛細live_workflow_runs

> 娉ㄦ剰锛氳繖鏄暟鎹簱璁捐鏂规銆傚綋鍓嶄笉鎵ц migration锛岀瓑浣犵‘璁ゅ悗鍐嶅缓琛ㄣ€?
| 瀛楁 | 绫诲瀷 | 璇存槑 |
| --- | --- | --- |
| `id` | uuid primary key | 鏃ュ織缂栧彿 |
| `company_id` | uuid not null | 鍏徃缂栧彿 |
| `platform_connection_id` | uuid null | 搴楅摵杩炴帴缂栧彿 |
| `agent_id` | uuid null | 鎵ц鐨?AI 鍛樺伐 |
| `workflow_name` | text not null | Workflow 鍚嶇О锛屼緥濡傚紑鎾墠妫€鏌?|
| `workflow_stage` | text not null | `pre_live` / `during_live` / `post_live` |
| `status` | text not null | `succeeded` / `blocked` / `needs_human` / `failed` |
| `input_snapshot` | jsonb not null default '{}' | 杈撳叆鏁版嵁蹇収锛岃劚鏁忓悗淇濆瓨 |
| `alerts` | jsonb not null default '[]' | 椋庨櫓鎻愰啋鍒楄〃 |
| `recommended_actions` | jsonb not null default '[]' | AI 寤鸿鍔ㄤ綔 |
| `human_action` | text null | 浜哄伐鏈€缁堝姩浣?|
| `human_feedback` | text null | 鍟嗗鍙嶉 |
| `saved_minutes` | integer not null default 0 | 鏈鑺傜渷鍒嗛挓鏁?|
| `saved_cost_yuan` | numeric(12,2) not null default 0 | 鏈鑺傜渷閲戦 |
| `risk_score` | integer not null default 0 | 椋庨櫓鍒?|
| `confidence` | numeric(5,4) null | AI 鍒ゆ柇缃俊搴?|
| `started_at` | timestamptz not null | 寮€濮嬫椂闂?|
| `finished_at` | timestamptz null | 缁撴潫鏃堕棿 |
| `created_at` | timestamptz not null default now() | 鍒涘缓鏃堕棿 |
| `updated_at` | timestamptz not null default now() | 鏇存柊鏃堕棿 |

## 寤鸿绱㈠紩

```sql
create index idx_live_workflow_runs_company_created
on live_workflow_runs(company_id, created_at desc);

create index idx_live_workflow_runs_company_stage
on live_workflow_runs(company_id, workflow_stage, created_at desc);

create index idx_live_workflow_runs_connection_created
on live_workflow_runs(platform_connection_id, created_at desc);
```

## RLS 鍘熷垯

1. 鐢ㄦ埛鍙兘璇诲彇鑷繁鎵€灞炲叕鍙哥殑鏃ュ織銆?2. 鐢ㄦ埛鍙兘鍐欏叆鑷繁鎵€灞炲叕鍙哥殑鏃ュ織銆?3. service_role 鍙互鎵ц鍚庡彴浠诲姟鍐欏叆銆?4. 鏃ュ織涓嶄繚瀛樺钩鍙拌闂护鐗屻€佽韩浠借瘉銆佸畬鏁村湴鍧€銆佹墜鏈哄彿鏄庢枃绛夐珮鏁忔劅鏁版嵁銆?
## Replay 鏂规硶

1. 璇诲彇鏌愪竴澶╃殑 `live_workflow_runs`銆?2. 鐢?`input_snapshot` 閲嶆柊璺戠洿鎾?Workflow銆?3. 瀵规瘮鏃х粨鏋滃拰鏂扮粨鏋溿€?4. 璁板綍椋庨櫓璇嗗埆鏄惁涓€鑷淬€佸缓璁姩浣滄槸鍚︽洿濂姐€佽妭鐪侀噾棰濇槸鍚﹀彉鍖栥€?
## Evaluation 鎸囨爣

| 鎸囨爣 | 璇存槑 |
| --- | --- |
| 椋庨櫓璇嗗埆鍑嗙‘鐜?| AI 鍙戠幇鐨勫簱瀛樸€佷紭鎯犲埜銆佽浆鍖栧紓甯告槸鍚︾湡瀹?|
| 浜哄伐閲囩撼鐜?| 鍟嗗鏄惁閲囩敤 AI 寤鸿 |
| 浜哄伐鎺ョ鐜?| AI 涓嶈兘鑷姩鍒ゆ柇鐨勬瘮渚?|
| 鑺傜渷鍒嗛挓鏁?| AI 鏇夸唬浜哄伐妫€鏌ュ拰鏁寸悊鐨勬椂闂?|
| 鑺傜渷閲戦 | 鑺傜渷鍒嗛挓鏁颁箻浠ュ矖浣嶅皬鏃舵垚鏈?|
| 澶嶇洏瀹屾垚鐜?| 姣忓満鐩存挱鏄惁鐢熸垚澶嶇洏 |

## 涓嬩竴姝ュ疄鐜板缓璁?
1. 鍏堟妸褰撳墠鍐呭瓨鏃ュ織鏇挎崲鎴愭暟鎹簱 repository銆?2. 鍐嶈鐩存挱妯℃澘瀵煎叆鍚庤嚜鍔ㄨ皟鐢ㄥ搴?Workflow銆?3. 鏈€鍚庢妸 Dashboard 鐨勮妭鐪侀噾棰濇敼涓鸿鍙栫湡瀹炴棩蹇楄仛鍚堛€?
## 浠ｇ爜杈圭晫宸插氨缁?
褰撳墠浠ｇ爜宸茬粡鏂板 `LiveWorkflowRunRepository` 浠撳偍鎺ュ彛锛屽苟灏嗗唴瀛樻棩蹇楀疄鐜板皝瑁呬负 `InMemoryLiveWorkflowRunRepository`銆傝繖鎰忓懗鐫€锛?
1. 鐜板湪鐨勭洿鎾?Workflow銆佽矾鐢卞拰 Savings Engine 涓嶅啀鐩存帴渚濊禆鍏ㄥ眬鍒楄〃銆?2. 鍚庣画纭鏁版嵁搴撹〃鍚庯紝鍙渶瑕佹柊澧?PostgreSQL/Supabase 浠撳偍瀹炵幇銆?3. API 鍜屽墠绔棤闇€鍥犱负鎸佷箙鍖栨柟寮忓彉鍖栬€岄噸鍐欍€?
浠嶉渶娉ㄦ剰锛氬綋鍓嶈繕娌℃湁鎵ц鏁版嵁搴?migration銆傜敓浜т娇鐢ㄥ墠蹇呴』纭琛ㄧ粨鏋勫苟瀹屾垚 Supabase 鎸佷箙鍖栥€?

## PostgreSQL 浠撳偍瀹炵幇瀛楁瑕佹眰

褰撳墠浠ｇ爜宸茬粡鏂板 `PostgresLiveWorkflowRunRepository`锛屼絾榛樿涓嶅惎鐢ㄣ€傚彧鏈夎缃細

```env
LIVE_WORKFLOW_LOG_STORAGE=postgres
```

骞朵笖 `DATABASE_URL` 鍙敤鏃讹紝鎵嶄細灏濊瘯鍐欏叆 `live_workflow_runs`銆?
涓轰簡鍏煎褰撳墠浠撳偍瀹炵幇锛岃〃缁撴瀯闇€瑕佸寘鍚互涓嬪瓧娈碉細

| 瀛楁 | 璇存槑 |
| --- | --- |
| `workflow_stage` | 瀵瑰簲棰嗗煙妯″瀷閲岀殑 `stage` |
| `approval_required` | 鏄惁闇€瑕佽€佹澘纭 |
| `proof` | 缁欒€佹澘棣栭〉鍜?Savings Engine 灞曠ず鐨勮瘉鎹彞 |
| `saved_cost_yuan` | 瀵瑰簲棰嗗煙妯″瀷閲岀殑 `estimated_saving_yuan` |
| `risk_score` | 褰撳墠浣滀负 Workflow 璇勫垎淇濆瓨 |
| `alerts` | JSONB 椋庨櫓鎻愰啋 |
| `recommended_actions` | JSONB 涓嬩竴姝ュ姩浣?|

娉ㄦ剰锛氬綋鍓嶄粛鏈墽琛屾暟鎹簱 migration銆傝〃缁撴瀯纭鍚庯紝鍐嶆妸璇ユ柟妗堣浆鎴?Supabase migration銆?

## 2026-07-15 本地 migration 状态

已新增本地 Supabase migration：`supabase/migrations/202607150001_live_workflow_runs.sql`。

当前状态：

1. 该 migration 尚未执行到线上 Supabase。
2. 后端默认仍使用内存仓储，避免未迁移生产库时影响试用控制台。
3. 执行线上迁移并配置 `LIVE_WORKFLOW_LOG_STORAGE=postgres` 后，直播 Workflow 日志即可持久化，用于老板首页省钱统计、CEO 日报和后续 Replay / Evaluation。
