# PubMed_Bot

> **EN** — An automated daily literature-surveillance pipeline. It searches PubMed across four clinical axes, keeps only high-quality journals (SCImago SJR Q1–Q2), summarises each article with Gemini, and routes the results to three destinations: Zotero, an email digest, and an Obsidian vault on Google Drive.
>
> **中文** — 每日自動化文獻追蹤系統。依四條臨床主軸搜尋 PubMed，只保留高品質期刊（SCImago SJR Q1–Q2），用 Gemini 產生中文摘要，再平行送往三個目的地：Zotero、Email 報告、Google Drive 上的 Obsidian 知識庫。

---

## 1. Features ｜ 功能特色

| EN | 中文 |
|----|------|
| Four independent search axes, each tagged on the result | 四條獨立搜尋主軸，結果自帶軸標籤 |
| Per-axis composable negative filters | 各軸可組合的負向過濾條件 |
| SCImago SJR Q1–Q2 journal-quality gate (runs *before* the expensive steps) | SCImago SJR Q1–Q2 期刊品質門檻（在耗資源步驟前先過濾） |
| Gemini summary + evidence rating, with automatic model fallback on overload | Gemini 摘要＋證據評級，過載時自動切換備援模型 |
| Branch A → Zotero · Branch B → Email · Branch C → Obsidian/Google Drive | A 分支→Zotero · B 分支→Email · C 分支→Obsidian/Google Drive |
| Runs unattended daily via GitHub Actions | 透過 GitHub Actions 每日無人值守執行 |

---

## 2. Architecture ｜ 系統架構

```
                 ┌─────────────────────────────────────────────┐
                 │  4 axes × independent PubMed search (mhda)   │
                 │  肺部疾病 / 感控 / 重症 / 博晟產品線          │
                 └───────────────────────┬─────────────────────┘
                                         │  union + axis tags
                                         ▼
                 ┌─────────────────────────────────────────────┐
                 │  SJR quality gate (SCImago Q1–Q2)            │
                 │  期刊品質門檻：低品質直接刷掉，省下後續成本   │
                 └───────────────────────┬─────────────────────┘
                                         │  survivors
                 ┌───────────────────────┼─────────────────────┐
                 ▼                       ▼                       ▼
        ┌────────────────┐     ┌──────────────────┐    ┌──────────────────┐
        │ Branch A       │     │ Branch B         │    │ Branch C         │
        │ Zotero ingest  │     │ Gemini → Email   │    │ .md → Google     │
        │ 書目存檔        │     │ 中文摘要報告      │    │ Drive (Obsidian) │
        └────────────────┘     └──────────────────┘    └──────────────────┘
```

**EN** — Searching is by **MeSH date (`mhda`)**, not entry date (`edat`): the query filters on `[PT]`/`[MH]` tags that are only assigned at indexing time, so `edat` would return ~0 every day.

**中文** — 搜尋用 **MeSH date（`mhda`）**，不是進站日（`edat`）。因為 query 依賴 `[PT]`/`[MH]` 標籤，而這些標籤要等編目索引完成才會掛上；用 `edat` 會每天抓到 0 篇。

---

## 3. Repository structure ｜ 專案結構

```
Pubmed_Bot/
├── pubmed_automation.py     # Main pipeline ｜ 主程式
├── sjr.py                   # SCImago SJR quartile lookup ｜ SJR 期刊分級查詢
├── get_refresh_token.py     # One-time local Google OAuth helper ｜ 本機一次性取得 Drive 授權
├── config/
│   └── settings.yaml        # Axes, negatives, SJR, report config ｜ 搜尋軸/負向/SJR/報告設定
├── data/
│   └── scimago.csv.gz       # SCImago journal table (gzipped) ｜ SCImago 期刊表（壓縮）
├── .github/workflows/
│   └── main.yml             # Daily GitHub Actions schedule ｜ 每日排程
├── .env.template            # Required secrets template ｜ 必填金鑰範本
└── requirements.txt
```

---

## 4. Prerequisites ｜ 環境需求

**EN**
- Python 3.10+
- A PubMed (NCBI) API key, a Gemini API key, a Zotero API key, a Gmail account (with an App Password) for sending mail, and a Google account whose Drive holds your Obsidian vault.

**中文**
- Python 3.10 以上
- 需備：PubMed (NCBI) API key、Gemini API key、Zotero API key、寄信用的 Gmail（需「應用程式密碼」），以及放 Obsidian 知識庫的 Google 帳號。

```bash
pip install -r requirements.txt
```

---

## 5. Secrets ｜ 金鑰設定

**EN** — Copy `.env.template` to `.env` for local runs, or add the same keys as **GitHub repository Secrets** for the scheduled run (Settings → Secrets and variables → Actions).

**中文** — 本機執行：把 `.env.template` 複製成 `.env` 填入；排程執行：到 **GitHub Repo → Settings → Secrets and variables → Actions** 加入同名 Secrets。

| Key ｜ 金鑰 | Purpose ｜ 用途 |
|------------|----------------|
| `PUBMED_API_KEY` | NCBI E-utilities key ｜ PubMed 搜尋 |
| `GEMINI_API_KEY` | Gemini summarisation ｜ Gemini 摘要 |
| `ZOTERO_API_KEY` / `ZOTERO_USER_ID` / `ZOTERO_COLLECTION_ID` | Branch A target ｜ Zotero 書目存檔目標 |
| `SENDER_EMAIL` / `SENDER_PASSWORD` / `RECEIVER_EMAIL` | Branch B email (Gmail App Password) ｜ Email 報告（Gmail 應用程式密碼） |
| `GDRIVE_CLIENT_ID` / `GDRIVE_CLIENT_SECRET` / `GDRIVE_REFRESH_TOKEN` / `GDRIVE_FOLDER_ID` | Branch C Google Drive (OAuth) ｜ Branch C Google Drive（OAuth） |

> **Note ｜ 注意** — Branch C uses **OAuth user credentials**, *not* a service account: a service account has no Drive storage quota on a personal Gmail and cannot upload. ｜ Branch C 用 **OAuth 個人帳號授權**，不是服務帳戶：服務帳戶在個人 Gmail 沒有 Drive 配額、無法上傳。

### 5.1 Google Drive OAuth (one-time) ｜ 取得 Drive 授權（一次性）

**EN**
1. Google Cloud Console → enable **Google Drive API**.
2. OAuth consent screen → **External**, add your own Gmail under **Test users**.
3. Credentials → **OAuth client ID** → type **Desktop app** → download the JSON as `credentials.json` into this folder.
4. Run the helper locally (it opens a browser):
   ```bash
   pip install google-auth-oauthlib
   python get_refresh_token.py
   ```
5. Copy the printed `GDRIVE_*` values into your Secrets. Get `GDRIVE_FOLDER_ID` from your vault folder's URL (`.../folders/THIS_PART`).

**中文**
1. Google Cloud Console → 啟用 **Google Drive API**。
2. OAuth 同意畫面 → 選 **External**，把自己的 Gmail 加進 **測試使用者**。
3. 憑證 → **OAuth 用戶端 ID** → 類型選 **桌面應用程式** → 下載 JSON 存成 `credentials.json` 放本資料夾。
4. 本機執行小工具（會跳出瀏覽器登入授權）：
   ```bash
   pip install google-auth-oauthlib
   python get_refresh_token.py
   ```
5. 把印出的 `GDRIVE_*` 值填進 Secrets。`GDRIVE_FOLDER_ID` 取自知識庫資料夾網址（`.../folders/這一串`）。

### 5.2 SCImago SJR data ｜ SJR 期刊資料

**EN** — The SJR gate needs the SCImago journal table. Download it once a year (it cannot be auto-downloaded — Cloudflare blocks bots):
1. Open <https://www.scimagojr.com/journalrank.php> → click **Download data**.
2. Save it as `data/scimago.csv`, then compress: `gzip -9 data/scimago.csv` → produces `data/scimago.csv.gz` (committed; the raw `.csv` is gitignored).

**中文** — SJR 門檻需要 SCImago 期刊表。一年下載一次（無法自動下載，Cloudflare 會擋機器人）：
1. 開 <https://www.scimagojr.com/journalrank.php> → 點 **Download data**。
2. 存成 `data/scimago.csv`，再壓縮：`gzip -9 data/scimago.csv` → 產生 `data/scimago.csv.gz`（進版控；原始 `.csv` 已 gitignore）。

---

## 6. Running ｜ 執行方式

**EN**
- **Locally**: `python pubmed_automation.py`
- **Scheduled**: GitHub Actions runs daily at **04:30 Taipei (UTC 20:30)**; you can also trigger it manually from the **Actions** tab (`workflow_dispatch`). GitHub schedules may run a few minutes late under load.

**中文**
- **本機**：`python pubmed_automation.py`
- **排程**：GitHub Actions 每天 **台北時間 04:30（UTC 20:30）** 自動跑；也可在 **Actions** 分頁手動觸發（`workflow_dispatch`）。GitHub 排程在高峰可能延遲幾分鐘。

---

## 7. How filtering works ｜ 篩選邏輯

**EN**
- **Axes** — `pulmonary / infection_control / critical_care / biosheng`. Each is searched independently; a PMID hit by several axes keeps all its tags.
- **Negatives** — composable subgroups (`nonhuman / pediatric / surgical / tcm / oncology`). The first three axes apply the full set; **biosheng omits `surgical`** (so implant/device topics aren't excluded).
- **SJR gate** — resolve the journal by ISSN against SCImago, take the best quartile across the matched-axis categories (with a **best-Q fallback** to the journal's overall best quartile), and keep **Q1–Q2** only.
- **Unindexed journals** — journals absent from SCImago pass through, flagged **`SJR：未收錄`** (no free/legal Impact-Factor source to fall back on).

**中文**
- **軸** — `肺部 / 感控 / 重症 / 博晟`。各自獨立搜尋；一篇被多軸命中會保留多個標籤。
- **負向** — 可組合子群（`nonhuman / pediatric / surgical / tcm / oncology`）。前三軸套完整負向；**博晟豁免 `surgical`**（避免擋掉植入物/器材主題）。
- **SJR 門檻** — 以 ISSN 對 SCImago 查期刊，取「該軸對應分類」的最佳分級（查不到時 **best-Q fallback** 用期刊整體最佳分級），只留 **Q1–Q2**。
- **未收錄期刊** — 不在 SCImago 的期刊照樣放行，標記 **`SJR：未收錄`**（IF 無免費合法來源可補）。

Each report (email + Obsidian note) shows the **journal, axis, and SJR grade**, and a `[Filter] N fetched → M passed` log distinguishes a genuinely empty day from a bug. ｜ 每份報告（Email＋Obsidian 筆記）都顯示 **期刊、領域軸、SJR 分級**；`[Filter] N fetched → M passed` 的 log 用來區分「合理的 0 篇」與「程式出錯的 0 篇」。

---

## 8. Configuration & maintenance ｜ 設定與維護

**EN**
- Edit search axes, keywords, negatives, SJR thresholds, and the Gemini model in **`config/settings.yaml`** — no code changes needed.
- `sjr_categories` names **must match the SCImago CSV exactly** (e.g. there is no "Tissue Engineering and Biomaterials" category).
- Refresh `data/scimago.csv.gz` once a year; re-run `get_refresh_token.py` if the Drive token is ever revoked.

**中文**
- 搜尋軸、關鍵字、負向、SJR 門檻、Gemini 模型都在 **`config/settings.yaml`** 調整，不必改程式。
- `sjr_categories` 名稱**必須與 SCImago CSV 完全一致**（例如並沒有「Tissue Engineering and Biomaterials」這個分類）。
- `data/scimago.csv.gz` 一年更新一次；Drive token 若被撤銷就重跑 `get_refresh_token.py`。

---

## License ｜ 授權

MIT License — see [LICENSE](LICENSE).
