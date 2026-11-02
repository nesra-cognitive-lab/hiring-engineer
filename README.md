# Nesra Scale - Software Engineer Take-Home Task

*Nesra, Surabaya. Please read the whole document before you start.*

## 1. Welcome

Thank you for your interest in joining Nesra. This task is a small, realistic version of a problem we solve every day. We want to see how you think, not how many hours you can spend.

- **Timebox:** about 3 to 4 hours of work.
- **Unfinished is OK.** If you run out of time, write down what is missing and how you would finish it.

## 2. About Nesra Scale

Nesra Scale is a marketing-data product. It collects shop, ads and sales data from marketplaces such as TikTok Shop and Shopee, and shows brands simple insights about their business.

In production we use **BigQuery + dbt** for data, **Prefect** for pipelines, and **Cloudflare Workers** for serving. BigQuery charges by how much data a query scans, so every unnecessary read costs real money. That is why this task is about one thing:

**Cost-aware caching: serve fast, correct reports while reading as little raw data as possible.**

## 3. The data

Data files: see [`data/`](data/) in this repository. The CSV files are gzip-compressed, and DuckDB reads `.csv.gz` directly.

- **`data/shops_90d.csv.gz`** - about 500 shops x 90 days of daily shop and product sales data. It is based on real data, but masked (names and IDs are changed).
- **`data/delta.csv.gz`** - new data that arrived after the first load. It contains new days, and also some **late corrections to older days**.
- **`data/data_dictionary.md`** - the exact column names, types and meanings.

Expected columns (one row = one product in one shop on one day):

| Column | Meaning |
| :---- | :---- |
| shop_id | Unique ID of the shop |
| shop_name | Shop display name |
| platform | Marketplace: TikTok Shop, Shopee or Tokopedia |
| date | Calendar date of activity (YYYY-MM-DD) |
| product_id | Unique ID of the product listing |
| product_name | Product display name |
| category | Product category |
| price | Average selling price per unit that day (Rp) |
| units_sold | Number of units sold that day |
| orders | Number of orders containing the product that day |
| revenue | Revenue that day (Rp), price x units_sold |
| ad_spend | Advertising spend attributed to the product that day (Rp) |
| views | Product impressions that day |
| clicks | Product clicks (detail-page visits) that day |

*Note: exact columns are in `data/data_dictionary.md`.*

**The data is real-world messy.** Look at it carefully before you trust it. Handle any problems in a sensible way, and write down what you found and what you decided.

## 4. What to build

Build a small service that runs on your laptop and has this endpoint:

```
GET /shops/{shop_id}/weekly-report?week=YYYY-Www
```

`week` is an ISO week, for example `2025-W11`.

The response must include:

| Field | Description |
| :---- | :---- |
| Revenue | Total revenue for the week |
| Units | Total units sold for the week |
| Week-over-week change | Change in revenue and units compared with the previous week |
| Top 5 products | The 5 best products of the week (explain how you rank them) |
| ROAS | Return on ad spend = revenue / ad_spend |
| Summary | A short plain-language summary of the week, for a brand owner |

The summary can come from a simple template. If you want, you can use an LLM instead, but this is **optional** and you do not need an API key. A good template is completely fine.

The JSON must include these top-level fields: `revenue` and `units` (integers), and `revenue_wow_pct` (a number, or `null` when there is no previous week to compare). You decide the rest of the format and how you handle edge cases. Explain your choices in the README.

## 5. Pretend the database is expensive

In this task, reading raw data is "expensive", like BigQuery.

- **All reads of raw data must go through one single function** (for example `scan_raw(...)`).
- That function must **log a simulated scan cost**: rows scanned x Rp 0.05 (a placeholder rate). Like a BigQuery table partitioned by date, a scan pays for every row in each date it reads, for all shops, even if you only need one shop.
- Your service must report the running totals at `GET /stats` as `{"rows_scanned": N, "cost_rp": N}`.

Do not read raw data anywhere else. Reads from your own cache or precomputed tables do not count as raw scans. Your cache must hold aggregated results (for example per shop and week), not a copy of the raw rows.

## 6. Budget goal

Imagine this production load:

- A weekly report is served for **all 500 shops, every day, for one month**.
- Each report is requested **20 times a day** (users refresh, share, open on mobile, and so on).

Your goal is to make this as cheap as possible. **To measure it, run [`measure.py`](measure.py) (in this repository) against your service. It requests weekly reports for every shop, calls `POST /load-delta`, requests them again, checks the answers and reads `GET /stats`. Target: under Rp 40,000 in total on that run. For scale, scanning raw data on every request costs tens of millions.**

Show your math in the README: the cost **before** caching (naive approach) and **after** caching, using the numbers `measure.py` reports.

## 7. Cache invalidation (the important part)

New data arrives after reports are already cached. You must:

1. Load `delta.csv.gz` when `POST /load-delta` is called. Return only when your reports are up to date.
2. Show that **affected reports refresh** and return the new correct numbers. This includes reports for **older weeks** that changed because of late corrections.
3. Show that **unaffected reports stay cached** and cost **nothing** to serve again.

A short demo script, test, or log output that proves this is very welcome.

## 8. Constraints

- **One command to run:** `docker compose up` or one script (for example `./run.sh`).
- **Any language.** We prefer Python or TypeScript.
- **Any local store:** DuckDB
- **Cache: DuckDB tables only, holding aggregated results.**
- **No cloud account needed.** Everything must run locally.

## 9. README requirements

Your README must include these sections:

- **Setup** - how to run it with one command, and how to call the endpoint.
- **Cache design** - what is cached, the cache keys, TTL vs event-based invalidation, and precompute vs on-demand.
- **Cost math** - simulated numbers before vs after caching, for the budget scenario in section 6.
- **When delta arrives** - step by step, what happens to the cache and the reports.
- **Data issues found** - what problems you found in the data and how you handled them.
- **Production mapping** - how your design would map to BigQuery + Cloudflare Workers.
- **With more time** - what you would improve or do differently.
- **AI tools note** - a short note on how you used AI tools (see below).

## 10. AI tools

AI tools (Codex, Claude Code, Cursor and others) are **allowed and expected**. We use them every day.

- Add a short note in your README on **how** you used them: which tools, for which parts, and what you changed or fixed yourself.
- You must be able to **explain and modify any line** of your code live in the interview.

We will talk about your AI workflow in the interview, not in this task.

## 11. How to submit

- Start from this repository: click **Use this template** on GitHub to create your own copy. It includes the data and `measure.py`.
- Push your work to a **GitHub repository**. It needs to be public.
- **Explain about your work** and why you choose to do that way in short video (loom, kommodo, etc).
- **Inform to the email / whatsapp this task came with** and include the repository link and short video link.

## 12. How we evaluate

| Area | Weight | What we look for |
| :---- | :---- | :---- |
| Cache design & invalidation correctness | 35% | Sensible keys, precise invalidation (including late corrections), no stale reports, unaffected reports stay cached |
| Cost reasoning & measured savings | 25% | Clear before/after math, real measured numbers, smart choices to reduce scans |
| Code quality & correctness of metrics | 20% | Readable code, correct revenue, units, WoW, top 5 and ROAS, reasonable tests |
| Data-issue handling | 10% | You noticed real problems, handled them sensibly, and documented your decisions |
| README communication | 10% | Clear, honest and easy to follow, including trade-offs and what is unfinished |

We value **clear thinking and honest trade-offs** more than lots of features.

## 13. What happens next

If your submission is a good fit, we will invite you to a **60-minute interview**:

- You walk us through your solution.
- We discuss how you work with AI tools.

## 14. Questions

If something is unclear, make a reasonable assumption, write it in your README, and continue. You can also reply to the email with questions.

Good luck, and have fun!
