# AI Commerce OS 鐢熶骇鎺ュ叆璇存槑

## 褰撳墠宸茬粡鍏峰鐨勮兘鍔?
- 鍟嗗鎺у埗鍙板凡缁忓彲浠ヤ綔涓虹綉椤典娇鐢ㄣ€?- FastAPI 鍚庣宸茬粡鍏峰 Docker銆丷ailway銆丷ender 閮ㄧ讲鏂囦欢銆?- 鍚庣鏀寔 Supabase PostgreSQL銆?- 鍚庣鏀寔瀹㈡湇娑堟伅妗ユ帴瀵嗛挜 `X-AICOS-Bridge-Key`銆?- 鍚庣鏀寔鐪熷疄瀹㈡湇娑堟伅杩涘叆 AI 瀹㈡湇鏀朵欢绠便€?- 鍚庣鏀寔鍟嗗搧銆佽鍗曘€佸鎴枫€佺墿娴併€佸敭鍚庢枃浠跺鍏ャ€?- 鍚庣鏀寔 `/health/ready` 鐢熶骇灏辩华妫€鏌ャ€?- 鍚庣鏀寔 `npm run api:bootstrap` 鐢熶骇鍒濆鍖栨鏌ャ€?
## 鍟嗗浠婂ぉ鎬庝箞鐢?
1. 鎵撳紑鍟嗗鎺у埗鍙般€?2. 杈撳叆搴楅摵鍚嶇О鍜屾墜鏈哄彿杩涘叆绯荤粺銆?3. 鍏堝湪鈥滃鍏ユ暟鎹€濅笂浼犲巻鍙插晢鍝併€佽鍗曘€佸鎴枫€佺墿娴併€佸敭鍚庢枃浠躲€?4. 鍦ㄢ€淎I瀹㈡湇鈥濋噷褰曞叆鎴栨ˉ鎺ョ湡瀹炲鎴锋秷鎭€?5. 浣庨闄╅棶棰樺彲浠ラ噰绾?AI 鑽夌銆?6. 閫€娆俱€佽禂鍋裤€佹姇璇夈€佸樊璇勩€侀噾棰濈浉鍏抽棶棰樺繀椤讳汉宸ョ‘璁ゃ€?7. 鍦ㄢ€滅渷閽辩粺璁♀€濇煡鐪嬭妭鐪佺殑浜哄伐鍒嗛挓鍜岄浼伴噾棰濄€?
## 鍚庣鐢熶骇閮ㄧ讲

Docker 鍚姩锛?
```bash
docker compose -f docker-compose.production.yml up -d --build
```

Railway 鎴?Render 閮ㄧ讲锛?
- Railway 浣跨敤鏍圭洰褰?`railway.json`
- Render 浣跨敤鏍圭洰褰?`render.yaml`

## 蹇呴』閰嶇疆鐨勭幆澧冨彉閲?
```text
SUPABASE_URL=
SUPABASE_PUBLISHABLE_KEY=
DATABASE_URL=
AUTH_REQUIRED=true
BACKEND_CORS_ORIGINS=https://ai-commerce-os-demo.ybqes.chatgpt.site,https://ai-commerce-os-internal.ybqes.chatgpt.site
MERCHANT_BRIDGE_API_KEY=
MERCHANT_BRIDGE_COMPANY_ID=
```

娉ㄦ剰锛?
- `DATABASE_URL` 蹇呴』鏄?Supabase PostgreSQL 鐨勭湡瀹炶繛鎺ヤ覆銆?- `MERCHANT_BRIDGE_API_KEY` 蹇呴』鏄珮寮哄害闅忔満瀵嗛挜銆?- 涓嶈鎶婃暟鎹簱瀵嗙爜銆乻ervice_role key銆佸钩鍙?app secret 鍙戝埌鑱婂ぉ绐楀彛閲屻€?
## 鐢熶骇鍒濆鍖?
鏁版嵁搴撹繛鎺ラ厤缃ソ浠ュ悗杩愯锛?
```bash
npm run api:bootstrap
```

杩欎釜鍛戒护浼氬仛鍥涗欢浜嬶細

1. 妫€鏌ユ暟鎹簱鑳戒笉鑳借繛鎺ャ€?2. 妫€鏌ユ牳蹇冭〃鍜屽瓧娈垫槸鍚﹀凡缁忔墽琛?migration銆?3. 鍒濆鍖栭粯璁ゅ叕鍙搞€丄I鑰佹澘銆丄I瀹㈡湇銆丄I鍞悗銆丄I杩愯惀銆?4. 鍒濆鍖栨窐瀹濄€佹姈闊炽€侀棽楸肩殑澶栭儴娑堟伅妗ユ帴杩炴帴銆?
濡傛灉杩斿洖锛?
```json
{
  "status": "ready",
  "database": true,
  "bridge_connection_ready": true
}
```

璇存槑鍚庣宸茬粡鍏峰鎺ユ敹鐪熷疄鍟嗗娑堟伅鐨勬潯浠躲€?
## 鐢熶骇灏辩华妫€鏌?
閮ㄧ讲鍚庤闂細

```text
/health/ready
```

杩斿洖锛?
```json
{
  "status": "ready",
  "database": true,
  "bridge_key": true
}
```

鎵嶈〃绀哄彲浠ユ帴鐪熷疄鍟嗗娑堟伅銆?
## 褰撳墠闃诲椤?
鐜板湪濡傛灉 `/health/ready` 杩斿洖 `database=false`锛岃鏄庡悗绔繕娌℃湁鐪熷疄 Supabase PostgreSQL 杩炴帴銆?
闇€瑕佸埌 Supabase 鍚庡彴澶嶅埗鐪熷疄 PostgreSQL 杩炴帴涓诧紝鍐欏叆锛?
- 鏈湴锛歚apps/api/.env`
- 浜戠锛歊ailway銆丷ender 鎴栧叾瀹冨悗绔儴缃插钩鍙扮殑鐜鍙橀噺

## 骞冲彴鎺ュ叆杈圭晫

娣樺疂銆佸ぉ鐚€佹姈搴椼€佹嫾澶氬蹇呴』浣跨敤瀹樻柟寮€鏀惧钩鍙版垨鍟嗗鎺堟潈鑳藉姏銆?
闂查奔褰撳墠鍙厑璁革細

- 鍟嗗鏂囦欢瀵煎叆
- 鍟嗗鑷湁鍚堣娑堟伅妗ユ帴

绂佹浣跨敤锛?
- Cookie 鎵樼
- 鎵爜浠ｇ櫥褰?- 鎶撳寘
- 闈炴巿鏉冪埇铏?
## 鎺ㄨ崘鐪熷疄璇曠偣鏂瑰紡

绗竴鎵圭湡瀹炲晢瀹朵笉瑕佷竴寮€濮嬭嚜鍔ㄥ洖澶嶃€?
鍏堜娇鐢細

- 鍘嗗彶鏁版嵁瀵煎叆
- 瀹㈡湇娑堟伅妗ユ帴
- AI 鑽夌
- 鍟嗗纭
- 瀛︿範璁板綍
- 鐪侀挶缁熻

褰撶湡瀹炴牱鏈揪鍒?300 鏉′互涓娿€佷綆椋庨櫓閿欒鐜囦綆浜?3% 鍚庯紝鍐嶅紑鍚綆椋庨櫓鑷姩鍥炲銆?
## 每日主动工作定时任务

生产环境必须让 AI 每天自动执行，而不是依赖老板手动点击。

当前已有三个入口：

1. 前端老板首页按钮：手动触发。
2. `npm run api:daily-operations`：本地或服务器命令触发。
3. Render Cron：每天北京时间早上 8 点自动执行。

生产启用前必须完成：

1. 在 Supabase 执行 `supabase/migrations/202607150001_live_workflow_runs.sql`、`202607160001_approval_records.sql`、`202607170001_after_sale_decision_outcomes.sql` 和 `202607180001_ceo_daily_report_snapshots.sql`。
2. 设置真实 `DATABASE_URL`。
3. 设置 `LIVE_WORKFLOW_LOG_STORAGE=postgres`、`APPROVAL_RECORD_STORAGE=postgres`、`AFTER_SALE_DECISION_STORAGE=postgres` 和 `CEO_REPORT_SNAPSHOT_STORAGE=postgres`。
4. 先导入真实商品、订单和售后数据，再运行 `npm run api:daily-operations`，确认返回 `status=completed` 且 `input_mode=merchant_payload`。

如果数据库未就绪，任务会返回 `blocked`，不会伪造 AI 已完成工作。
