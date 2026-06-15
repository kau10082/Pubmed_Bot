# PubMed_Bot 🩺📚

*A self-hosted **PubMed literature-alert** bot — automated daily **literature monitoring / surveillance** with **AI summaries**, a free alternative to PubMed email alerts / RSS, routed to **Zotero**, **email**, and **Obsidian**.*
*自架的 **PubMed 文獻訂閱 / 追蹤機器人**：每日自動監測新文獻、AI 摘要，PubMed Email Alert／RSS 的替代方案，輸出到 Zotero、Email、Obsidian。*

> **中文** — 每天自動從 PubMed 找出你關注領域的高品質醫學新論文，用 AI 寫成中文摘要，再寄到你的信箱、存進 Zotero、並同步成 Obsidian 筆記。讓你每天早上一杯咖啡的時間就掌握最新文獻，不必自己一篇篇翻。
>
> **EN** — Every day this bot finds new, high-quality medical papers on PubMed in the fields you care about, writes a Chinese summary with AI, and delivers them to your inbox, Zotero, and Obsidian. Stay on top of the literature in the time it takes to drink your morning coffee.

---

## 你會收到什麼？ ｜ What you get

每天一封 email，開頭是**當日總覽**，接著是**每篇文章的詳細中文摘要**：

Each day, one email: a **daily overview** at the top, followed by a **detailed Chinese summary of every paper**.

```
🔍 搜尋過程摘要   肺部 3 篇 | 感控 1 篇 | 重症 2 篇 | 博晟 0 篇 | 戒菸 1 篇
                合計 6 篇 → 通過品質門檻 4 篇（刷掉 2 篇）
📋 今日文章摘要   1. 某藥顯著降低住院率…  [PubMed]
                2. 某療法對死亡率無益…   [PubMed]
─────────────────────────────────
（每篇：標題、期刊、SJR 分級、研究方法、樣本數、中文摘要、原文摘要）
```

同時（可開關）：論文存進 **Zotero** 書目庫、生成 **Obsidian** 筆記（`.md`）同步到 Google Drive。

Optionally: papers are also saved to **Zotero** and turned into **Obsidian** notes synced via Google Drive.

---

## 運作原理（一分鐘版） ｜ How it works (1-min version)

```
每天抓 PubMed 新文獻（5 條主題線各自搜尋）
        │
        ▼
品質門檻：只留 SCImago SJR 高分期刊（Q1 / 部分線 Q1+Q2）
        │
        ▼
通過的文章 → 三條輸出分支（可各自開關）
   ├─ A · Zotero 書目存檔
   ├─ B · Gemini 中文摘要 → Email
   └─ C · Obsidian 筆記 → Google Drive
```

五條主題線（可自訂）：**肺部疾病、感控、重症、博晟產品線、戒菸**。
Five topic lines (configurable): pulmonary, infection control, critical care, the Biosheng product line, and smoking cessation.

> 小技術點：搜尋用 PubMed 的 **MeSH date（mhda）**，文章才會帶有研究類型與主題標籤；多數主題線用 **MeSH 主要主題詞**，確保抓到的是「主題就是這個」的文章，而不是順口提一句。

---

## 安裝方法 ｜ Installation

### 你需要先準備 ｜ What you'll need first

- **Python 3.10 以上** ｜ Python 3.10+
- 幾組免費/付費的 API 金鑰（下方第 3 步逐一說明）｜ a few API keys (explained in step 3)
- 一個 Gmail（用來寄信）＋ 放 Obsidian 筆記的 Google 帳號 ｜ a Gmail (to send) and a Google account for the Obsidian vault

### 步驟 ｜ Steps

**1. 下載專案、安裝套件 ｜ Clone & install**
```bash
git clone https://github.com/kau10082/Pubmed_Bot.git
cd Pubmed_Bot
pip install -r requirements.txt
```

**2. 下載期刊品質資料（SCImago，一年一次）｜ Get the journal-quality data (once a year)**
- 打開 <https://www.scimagojr.com/journalrank.php> → 點 **Download data**
- 存成 `data/scimago.csv`，再壓縮：`gzip -9 data/scimago.csv`（產生 `data/scimago.csv.gz`）
- ｜ Open the link, click **Download data**, save as `data/scimago.csv`, then `gzip -9 data/scimago.csv`.

**3. 準備金鑰、填進 `.env` ｜ Fill in your keys**

把 `.env.template` 複製成 `.env`，填入以下值。本機測試用 `.env`；正式排程則改放 **GitHub Secrets**（見第 5 步）。
Copy `.env.template` to `.env` and fill these in. Use `.env` for local testing; for the scheduled run put them in **GitHub Secrets** (step 5).

| 金鑰 ｜ Key | 用途 ｜ What it's for | 去哪拿 ｜ Where |
|---|---|---|
| `PUBMED_API_KEY` | 搜尋 PubMed ｜ search PubMed | NCBI 帳號 → Account Settings |
| `GEMINI_API_KEY` | AI 寫摘要 ｜ AI summaries | Google AI Studio |
| `ZOTERO_API_KEY` / `ZOTERO_USER_ID` / `ZOTERO_COLLECTION_ID` | 存書目（可關）｜ save to Zotero (optional) | Zotero → Settings → Feeds/API |
| `SENDER_EMAIL` / `SENDER_PASSWORD` / `RECEIVER_EMAIL` | 寄信／收信 ｜ send/receive mail | Gmail「應用程式密碼」｜ Gmail App Password |
| `GDRIVE_CLIENT_ID` / `GDRIVE_CLIENT_SECRET` / `GDRIVE_REFRESH_TOKEN` / `GDRIVE_FOLDER_ID` | 寫 Obsidian 筆記（可關）｜ Obsidian notes (optional) | 見第 4 步 ｜ see step 4 |

**4. 設定 Google Drive 授權（一次性）｜ Authorize Google Drive (one-time)**

> 為什麼是這串步驟？因為機器人要用「你本人」的身分把筆記寫進你自己的 Drive。（服務帳戶在個人 Gmail 沒有空間配額，無法上傳，所以改用 OAuth。）
> Why these steps? The bot writes notes into *your* Drive as *you* (a service account has no storage quota on a personal Gmail, so we use OAuth).

1. Google Cloud Console → 啟用 **Google Drive API** ｜ enable the Google Drive API
2. OAuth 同意畫面選 **External**，把自己的 Gmail 加進 **測試使用者** ｜ consent screen = External, add your Gmail as a test user
3. 建立 **OAuth 用戶端 ID → 桌面應用程式**，下載 JSON 存成 `credentials.json` 放專案資料夾 ｜ create an OAuth client ID (Desktop app), save the JSON as `credentials.json`
4. 本機跑一次（會開瀏覽器登入）：
   ```bash
   pip install google-auth-oauthlib
   python get_refresh_token.py
   ```
5. 把畫面印出的 `GDRIVE_*` 值填進 `.env`／Secrets。`GDRIVE_FOLDER_ID` 是你 vault 資料夾網址 `.../folders/` 後面那串。
   Copy the printed `GDRIVE_*` values into your keys. `GDRIVE_FOLDER_ID` is the part after `.../folders/` in your vault folder's URL.

**5. 設定每日自動執行 ｜ Schedule the daily run**

把第 3、4 步的所有金鑰加到 GitHub：Repo → **Settings → Secrets and variables → Actions → New repository secret**（名稱與 `.env` 完全相同）。之後 GitHub Actions 會**每天台北時間 04:30** 自動跑。
Add every key as a **GitHub repository Secret** (same names as in `.env`). GitHub Actions then runs **daily at 04:30 Taipei time**.

---

## 使用方法 ｜ Usage

**每日自動** ｜ **Automatic** — 設好 Secrets 後就不用管，每天 04:30 自動寄信。
Once Secrets are set, it just runs every day at 04:30 — nothing to do.

**手動跑一次（可臨時開關分支）** ｜ **Run manually (with per-run branch toggles)**
GitHub → **Actions** 分頁 → 選 **PubMed_Bot Daily Report** → **Run workflow**。會看到三個下拉，可把 Zotero／Email／Google Drive 任一條臨時設 `on`／`off`（選 `default` 就照設定檔）。
In the **Actions** tab → **Run workflow**: three dropdowns let you turn Zotero / Email / Google Drive `on`/`off` just for that run (`default` = use the config file).

**本機跑** ｜ **Run locally**
```bash
python pubmed_automation.py
# 臨時關掉某條分支 ｜ turn a branch off for this run:
RUN_ZOTERO=off python pubmed_automation.py
```

---

## 設定方法 — `config/settings.yaml` ｜ Configuration

所有可調的東西都在這個檔，**不用改程式**。Everything tunable is here — no coding needed.

### 開關各條輸出分支 ｜ Turn output branches on/off

文獻太多、不想每天整理 Zotero？把它關掉就好（預設已關）：
Too many papers to curate in Zotero? Just switch it off (it's off by default):

```yaml
branches:
  zotero: false   # A · Zotero（預設關 ｜ off by default）
  email: true     # B · Email
  gdrive: true     # C · Obsidian / Google Drive
```
> 這是**持久設定**（影響每日排程）。想單次臨時改，用上面〈使用方法〉的 Actions 下拉或 `RUN_ZOTERO=off`。
> This is the **persistent** default (affects the daily run). For a one-off change, use the Actions dropdowns or `RUN_ZOTERO=off`.

### 新增／修改一條主題線 ｜ Add or edit a topic line

`query.axes` 底下每一筆就是一條獨立搜尋線。複製一塊、改四個欄位即可：
Each entry under `query.axes` is one independent search. Copy a block and edit four fields:

```yaml
  axes:
    - key: cardiology                 # 內部代號（唯一）｜ unique id
      name: '心臟科'                   # 報告顯示的名字 ｜ display name
      core: '("Heart Failure"[Majr] OR arrhythmia)'   # 搜尋詞（PubMed 語法）｜ search query
      negatives: [nonhuman, pediatric]  # 套哪些排除組 ｜ which exclusion groups
      sjr_categories: ['Cardiology and Cardiovascular Medicine']  # SCImago 分類（須與 CSV 完全一致）
      allowed_quartiles: ['Q1', 'Q2']   # 選填：覆寫品質門檻 ｜ optional: override the quality bar
```
> 想抓得準、不浮濫，搜尋詞建議用 **`"術語"[Majr]`（MeSH 主要主題詞）**，代表「文章主題就是這個」。
> For precision, prefer **`"Term"[Majr]`** (MeSH Major Topic) — it means the paper is *primarily about* that term.

### 排除條件 ｜ Exclusion groups

`query.negatives` 定義可重用的排除組，各線用 `negatives:` 挑要套哪些：
Reusable exclusion groups; each line picks which to apply:

| 組 ｜ Group | 排除 ｜ Excludes |
|---|---|
| `nonhuman` | 動物 / 細胞 / in vitro ｜ animal / cell / in vitro |
| `pediatric` | 兒科 ｜ pediatric |
| `surgical` | 手術 / 麻醉 ｜ surgery / anaesthesia |
| `tcm` | 中醫藥 ｜ traditional Chinese medicine |
| `oncology` | 肺癌 ｜ lung cancer |

### 品質門檻 ｜ Quality gate

```yaml
sjr:
  enabled: true
  allowed_quartiles: ['Q1']   # 全域預設：只收 Q1 ｜ global default: Q1 only
  include_unindexed: true     # 不在 SCImago 的期刊照收（標「未收錄」）｜ keep journals absent from SCImago
```
各線可用 `allowed_quartiles` 覆寫（例如博晟、戒菸線設 `['Q1','Q2']` 放寬）。一篇文章只要通過**任一命中線**的門檻就保留。
A line can override `allowed_quartiles` (e.g. biosheng & smoking lines use `['Q1','Q2']`). An article passes if it clears **any** of its matched lines' bars.

### 其他常用旋鈕 ｜ Other handy knobs

| 設定 ｜ Setting | 預設 ｜ Default | 作用 ｜ What it does |
|---|---|---|
| `search.lookback_days` | `1` | 搜尋幾天內的文獻（1＝昨天）｜ how many days back |
| `search.per_article_delay_seconds` | `13` | 每篇間隔秒數（付費 API 可調小加速）｜ delay per article |
| `report.gemini_model` | `gemini-2.5-flash` | 摘要用的 AI 模型（過載會自動換備援）｜ summary model (auto-fallback) |
| `report.language` | `zh-TW` | 摘要語言 ｜ summary language |
| `report.smtp_host` / `smtp_port` | Gmail | 寄信伺服器（非 Gmail 可改）｜ mail server |

---

## 維護 ｜ Maintenance

- 每年更新一次 `data/scimago.csv.gz`（見安裝第 2 步）｜ Refresh the SCImago file yearly (install step 2).
- Google Drive 授權若失效，本機重跑 `python get_refresh_token.py`｜ If the Drive token expires, re-run `get_refresh_token.py`.

---

## 資料來源與標註 ｜ Data source & attribution

`data/scimago.csv.gz` 為 [SCImago Journal & Country Rank](https://www.scimagojr.com/)（SJR）**2025 年版**，源自 Elsevier Scopus，著作權屬 SCImago / Scopus，**僅供非商業學術／個人用途**，不受本專案 MIT 授權涵蓋。
`data/scimago.csv.gz` is the **2025** [SCImago Journal & Country Rank](https://www.scimagojr.com/) dataset (from Elsevier Scopus), © SCImago / Scopus, bundled **for non-commercial academic/personal use only** and not covered by this project's MIT license.

## 授權 ｜ License

MIT（**僅程式碼**；SCImago 資料見上）｜ MIT License — see [LICENSE](LICENSE) (**code only**; SCImago data excluded, see above).
