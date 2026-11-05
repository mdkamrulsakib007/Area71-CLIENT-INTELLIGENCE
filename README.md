# Area71 MPS Client Intelligence

**Fresh rebuild from `MPS Client Updates (NEW).xlsx` — November 2026**

A private, single-user database and browser dashboard for Area71's Managed Partner Service (MPS) Operations and Sales workflows. It requires **Python 3.9+ only**; no paid AI subscription, API key, Node.js, or other packages are required to run the dashboard.

## Start on your Mac

1. Download and extract the ZIP. Keep the entire `Area71_MPS_Intelligence` folder together.
2. Open **Terminal** and navigate into that folder (in Finder, drag the extracted folder into Terminal after typing `cd `).
3. Run:

   ```bash
   python3 server.py
   ```

4. Visit **http://127.0.0.1:8765** (normally opens automatically). Keep Terminal running while you use it.
5. Close the app with **Control+C** in Terminal.

Alternatively, from Finder open `start_mac.command`. If macOS blocks it, use Terminal as above.

For Windows, run `start_windows.bat` or `py -3 server.py` from the extracted folder. If port 8765 is busy, on a Mac run `AREA71_PORT=8766 python3 server.py` and open `http://127.0.0.1:8766`.

## Dashboard sections

| Section | What it does |
| --- | --- |
| Overview | Client and product counts, recorded marketplace totals, pipeline statuses, source confidence. |
| Product records | Search/filter the 592 imported products; edit one product at a time; create products; archive/restore. |
| Client directory | Manage the 183 explicit client profiles and recorded communications. |
| **Tool 1 — Anomaly Guard** | Rule-driven reviews for shipping/compliance holds, high ACOS, formula errors, unverified client links, and sales reconciliation; assign owners, update statuses, and record findings. |
| **Tool 2 — Ask the Data** | Ask supported plain-English questions (marketplace performance, blocked products, highest ACOS, top products, PPC specialists, restock, or client IDs); receive a calculated table/visual. |
| **Tool 3 — Client Brief** | Generate a client-facing preparation brief with product portfolio, recorded notes, risks, and follow-up suggestions. |
| Source archive | View original rows and formulas for all six worksheets, without changing their historical values. |
| Activity history | Audits edits, notes, archive changes, and alert reviews. |

**Note:** These are *local AI-assisted workflow tools*, implemented as transparent rule-based analytics and a constrained natural-language parser. They do not invoke a generative AI model, understand arbitrary natural-language questions, predict future performance, or connect to Amazon. This limitation is deliberate so the pilot works fully offline, with auditable arithmetic and no data leaving your computer.

### Examples for Ask the Data

- `Sales versus ad spend by marketplace`
- `Show blocked products in UAE`
- `Highest ACOS products`
- `Top 10 products by sales`
- `Live products by marketplace`
- `PPC performance by specialist`
- `Which products need restock?`
- `Client MPS-28724-02`

The app provides an error message if a question is outside the supported set.

## Source and integrity approach

- Canonical import: `MPS Client Info`, **592 product rows**, **183 explicitly recorded client IDs**, **35 original columns**.
- The five other original worksheets are **archived, not double-counted** in totals. The unchanged source XLSX is in `originals/`.
- Product/client linking: **422 explicit IDs**, **161 confirmed via merged-cell ranges**, **9 inferred from neighboring rows**. The final nine are flagged for review and must be confirmed before account-specific decisions.
- **142 review alerts at import**, including **39 original `#DIV/0!` TACOS formula errors**. Alerts indicate **items for human verification**, not proven losses or permission to pause campaigns.
- Calculated metrics use **Y = total sales, Z = ad-attributed sales, AA = recorded organic sales, AB = ad spend**, based on the verified NEW-source layout. **ACOS = AB / Z**; **TACOS = AB / Y**; **ad ROAS = Z / AB**. Undefined ratios are blank, never treated as zero.
- A genuine source reconciliation difference in original **row 530** and a TACOS scaling discrepancy in **row 194** are documented in the original-source archive and included in the review queue.
- The source's EXW and shipping prices may use mixed currencies and free text. These values are **preserved, not automatically converted**. The dashboard does not claim to calculate net profit or a validated margin.
- The dashboard uses the *uploaded historical snapshot*. It is **not live Seller Central data**; recorded sales may represent different time periods.

## Editing, exports, and backups

1. Use **Product records** or **Client directory** for changes. The source archive remains unchanged.
2. Changes are saved immediately into `data/mps_intelligence.sqlite` and captured in the **Activity history**.
3. The app recalculates derived metrics and refreshes rule alerts after edits.
4. Use **Create database backup** from the sidebar regularly; this writes a timestamped `.sqlite` file to `backups/`. Keep additional copies of that folder in a secured company location.
5. Download CSV snapshots from the dashboard as needed.

The included `docs/Area71_Fresh_MPS_Client_Database.xlsx` is a **snapshot** created at import. Editing the workbook directly **does not automatically sync** changes back to the SQLite application, and changing the live SQLite database **does not automatically update that workbook**. Export current CSV records after updates, or implement a deliberate import/export workflow before adopting Excel-based editing.

## Files and folders

```text
Area71_MPS_Intelligence/
  server.py, core.py           Local application and analytics logic
  static/                      Browser interface
  data/mps_intelligence.sqlite Editable database (KEEP PRIVATE)
  originals/                   Unmodified uploaded source workbook
  docs/                        Refined Excel snapshot, slide presentation, source audit, previews
  scripts/test_application.py  Offline regression tests (mutate temporary DB copies only)
  scripts/build_presentation.js Source deck builder; NOT required to run the dashboard
  backups/                     User-created local backups
  start_mac.command, start_windows.bat
```

For a quick health check, run `python3 scripts/test_application.py`; the 15 regression tests use temporary database copies, not the live data.

## Privacy, access, and deployment

The app binds to `127.0.0.1` (your own device), rejects non-local `Host` requests, and never sends data to external services. **There is no user login, role permissions, encryption at rest, automatic cloud backup, or multi-user synchronization.** Do not expose this server to the internet, deploy it to Cloudflare Pages as a static site, or share the ZIP and its live database publicly. The SQLite file contains client details and notes.

For Area71-wide use, a separate production phase should add authenticated accounts, role-based access, protected hosting, encrypted backups, and review/approval of any Amazon/Meta/Google integrations. The current application is a functional **private single-user pilot**.

## Dependencies and source

- Runtime: Python 3.9+ standard library, any modern browser
- No API key, service account, network access, or external dependencies required to run
- Source: `originals/MPS Client Updates (NEW).xlsx` only
- Verification: database `PRAGMA integrity_check`, 15 unit/regression tests, presentation overflow check, workbook formula/cached value review
