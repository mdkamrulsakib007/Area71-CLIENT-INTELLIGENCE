# Fresh-source import and QA report

Source workbook: `MPS Client Updates (NEW).xlsx`

- SHA-256 matches unmodified bundled source: `a858d1b6dbd81e9d0827d6e2afe2549f819d3e9a23d08e0cf8c058c20f8ad732`
- Canonical tab: `MPS Client Info`; other five tabs included in source archive only
- Client profiles: **183**
- Main product entries: **592**
- Recorded markets: **6**
- Original source columns: **35**
- Client associations: **422 explicit**, **161 merged-cell**, **9 neighbor-inferred** (review needed)
- Import-time rule alerts: **142**, consisting of **46 critical**, **39 high**, **57 medium**; 39 of these are original source TACOS formula errors, not new calculated failures
- Financial mapping: **Y Total Sales, Z Ad Sales, AA Organic Sales (recorded), AB Ad Spend**
- Recorded totals, not live: **$494,956.88 total sales**, **$273,969.87 ad-attributed sales**, **$79,008.97 ad spend**
- Known source-review items: source row 530 organic sales reconciliation, row 194 TACOS scaling, nine inferred associations

### Tests performed

1. Offline application regression suite: **15 passed**.
2. HTTP smoke test using a **disposable database copy**: health, client/products, alerts, language query, client brief, update and audit log, backup: passed.
3. SQLite integrity check: `ok`.
4. PowerPoint: 18 slides, rendered and canvas-overflow check passed.
5. Excel: nine tabs, calculated finance formulas and marketplace cache values inspected. Historical source formula errors are preserved as such, not silently overwritten; some intentionally blank derived formula values have blank caches.
6. Original workbook: the bundled `originals/` copy matches uploaded bytes exactly.

### Non-goals / limitations

- No real-time Amazon, ad-platform, Meta Pixel, Sheets, email, or WhatsApp integration.
- No unrestricted generative AI model; the language interface recognizes a transparent, fixed set of questions.
- No currency conversion or authoritative profitability calculation from mixed-currency costs.
- No public hosting, accounts, staff permissions, automated synchronization, or daily cloud backups.
- Spreadsheet snapshot and local app do not live-sync. Use the dashboard as the editable pilot source of truth.
- Alerts are screening checks requiring human verification, not guaranteed factual diagnoses.
