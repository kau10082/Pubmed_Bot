# `data/` — SCImago SJR dataset ｜ SCImago SJR 資料

**`scimago.csv.gz`**

| | |
|---|---|
| Source ｜ 來源 | [SCImago Journal & Country Rank](https://www.scimagojr.com/) (derived from Elsevier Scopus) |
| Edition ｜ 版本 | **2025** |
| Format ｜ 格式 | gzipped, semicolon-delimited CSV ｜ gzip 壓縮、分號分隔 CSV |
| Used by ｜ 用途 | `sjr.py` — journal Q1–Q2 quality gate ｜ 期刊 Q1–Q2 品質門檻 |
| Copyright ｜ 著作權 | © SCImago / Scopus — **non-commercial use only**; not covered by the repo's MIT license ｜ 著作權屬 SCImago / Scopus，**僅供非商業用途**，不受本專案 MIT 授權涵蓋 |

## Updating ｜ 更新方式

**EN** — Once a year: download the latest table from <https://www.scimagojr.com/journalrank.php> ("Download data"), save as `data/scimago.csv`, then `gzip -9 data/scimago.csv`. The raw `.csv` is gitignored; only the `.gz` is committed.

**中文** — 每年一次：到 <https://www.scimagojr.com/journalrank.php> 點「Download data」下載最新表，存成 `data/scimago.csv`，再 `gzip -9 data/scimago.csv`。原始 `.csv` 已 gitignore，只 commit `.gz`。
