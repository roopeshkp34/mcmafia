---

# PRD: Forensic Equity (FE-v1.0)

**Project Code:** "Divergence Engine"

**Target Audience:** Engineering, Forensic Accountants, Institutional Fund Managers

**Core Objective:** To identify the "Say-Do Gap"—the delta between management's qualitative narrative and the quantitative reality of their financial filings.

---

## 0. Executive Summary

Forensic Equity is a specialized financial intelligence platform designed for HNW individuals and Fund Managers. It utilizes a **Stateful Multi-Agent System** and **GraphRAG** to identify "Narrative Divergence"—instances where qualitative management claims are contradicted by quantitative financial data.

## 1. The Forensic Schema: 25 Red Flag Categories

The "Forensic Critic" agent uses these specific patterns to scan the Neo4j Knowledge Graph and Vector Store.

| # | Category | The "Smoke" (Quant Signal) | The "Mirror" (Qual Narrative) | Logic Trigger |
| --- | --- | --- | --- | --- |
| 1 | Revenue Pull-Forward | DSO↑ while Revenue is flat. | Focus on "Strategic channel wins." | DSO>1.25× Peer Avg. |
| 2 | Inventory Bloat | Finished Goods ↑ vs. Sales ↓ | "Supply chain resilience prep." | Inventory growth > Sales + 15%. |
| 3 | Expense Shifting | "Other Assets" spike suddenly. | "Investments in efficiency." | Unexplained Asset spike > 5% TA. |
| 4 | Quality of Earnings | Net Income (+) but OCF (-) | "Focus on non-cash growth." | 3 Qtrs of OCF < Net Income. |
| 5 | Margin Compression | COGS as % of Rev ↑ | "Operating leverage" claims. | Margin erosion while claiming "Scale." |
| 6 | Executive Churn | CFO/CAO/Auditor exit nodes. | "Pursuing personal interests." | Exit within 90 days of 10-K. |
| 7 | Liability Masking | Contingent Liab. text length ↑ | Removal of specific risk keywords. | Textual deletion of known risks. |
| 8 | Capitalized OpEx | PPE/Sales↑ unexpectedly. | "Proprietary tech development." | Shift of OpEx keywords to CapEx. |
| 9 | Goodwill Mirage | Mkt Cap < Book Value. | "Intangible brand strength." | Impairment not taken despite Δ. |
| 10 | Pension Smoothing | Discount rate node ↑ | "Prudent actuarial assumptions." | Rate Δ>50bps vs. Peers. |
| 11 | R&D Capitalization | R&D Exp ↓ while Intangibles ↑ | "Efficiency in R&D pipeline." | Capitalizing > 20% of R&D spend. |
| 12 | Restructuring Addiction | "One-time" charges for 3+ yrs. | "Finalizing the pivot." | Recurring "Non-recurring" items. |
| 13 | Vendor Financing | Accounts Payable ↑ vs. COGS ↔ | "Favorable vendor terms." | AP growth 2× COGS growth. |
| 14 | Lax Credit Quality | Allowance for Doubtful Accts ↓ | "High quality customer mix." | Allowance % ↓ while AR↑. |
| 15 | Related Party Loop | Transactions with affiliated nodes. | "Strategic partnerships." | Entities with shared board nodes. |
| 16 | Tax Strategy Drift | Eff. Tax Rate vs. Statutory Δ↑ | "Jurisdictional optimization." | ETR < 10% without 8-K justification. |
| 17 | Buyback Smoke | Buybacks ↑ while Debt ↑ | "Returning value to shareholders." | Debt-funded share repurchases. |
| 18 | Glossary Drift | Change in "Non-GAAP" definitions. | "Aligning metrics with strategy." | Mathematical formula Δ YoY. |
| 19 | Footnote Obfuscation | Sentence complexity in Footnotes ↑ | "Detailed disclosure." | Gunning Fog Index > 18 in Notes. |
| 20 | Asset Stuffing | "Prepaid Expenses" ↑ vs. OpEx | "Strategic prepayments." | Growth > 3σ from mean. |
| 21 | Audit Fee Squeeze | Audit Fees ↓ while Complexity ↑ | "Focus on cost-efficiency." | Fee ↓ during M&A activity. |
| 22 | Backdated Accruals | Prior period adjustments ↑ | "Standardizing historical data." | Net Income restatements > 2%. |
| 23 | Off-Balance Sheet | SPV/VIE node complexity ↑ | "Strategic minority interests." | Total assets in VIE > 10% of Parent. |
| 24 | Linguistic Hedging | Increase in "might," "could," "perhaps." | Vague future outlook. | Hedge-word density ↑ 30% YoY. |
| 25 | Beneish M-Score | Mathematical fraud probability. | High sentiment/Bullish tone. | M-Score > -1.78 + High Sentiment. |

---

## 2. 20 Target User Stories

### Phase 1: Ingestion & Structural Mapping

- **US.1:** As a user, I want to upload multiple 10-K/10-Q PDFs so they can be parsed into a structured Markdown/JSON hierarchy via **LlamaParse**.
- **US.2:** As an analyst, I want a **"Deep Trace"** feature where clicking any financial node shows the original PDF page with a bounding box around the source data.
- **US.3:** As a developer, I want all financial line items mapped to a **Unified Taxonomy** (e.g., "Net Sales" and "Total Revenue" map to the same UUID).
- **US.4:** As a QA engineer, I want an **"Ingestion Health Report"** that flags if a balance sheet fails to balance ($Assets = Liabilities + Equity$) before analysis begins.
- **US.5:** As a user, I want the system to automatically extract and link "Note" references (e.g., "See Note 4") to the corresponding footnote text in the graph.

### Phase 2: The Divergence Engine (Logic & AI)

- **US.6:** As a fund manager, I want a **"Linguistic Drift"** alert when management removes specific risk-related keywords they used in the previous year.
- **US.7:** As an analyst, I want a **Split-Screen "Reality Check"** view comparing a Management Claim (Left) against a 3-year Financial Trend chart (Right).
- **US.8:** As a user, I want the **"Forensic Critic" (o1 Agent)** to flag contradictions between a Q2 Earnings Call transcript and a Q3 10-Q filing.
- **US.9:** As an auditor, I want to identify when "Non-GAAP" metrics are adjusted in a way that turns a GAAP loss into an "Adjusted" gain.
- **US.10:** As a user, I want a **"Sentiment-Reality Heatmap"** showing sectors where management tone is most decoupled from actual margin performance.

### Phase 3: Graph-Based Deep Dive

- **US.11:** As a user, I want to query the graph for **"Executive Churn"** and see a timeline of departures overlaid on the stock price and auditor changes.
- **US.12:** As an analyst, I want to find **"Hidden Peer Risks"** by identifying risk factors mentioned by 3+ competitors that my target company has omitted.
- **US.13:** As a fund manager, I want a **Knowledge Graph Visualization** of subsidiary relationships to detect potential "Circular Cash Flows."
- **US.14:** As a user, I want to search for "Accounting Skeletons" (e.g., "Special Purpose Vehicles") across the entire S&P 500 vector store simultaneously.
- **US.15:** As an analyst, I want to see a **"Director Network"** graph to identify "Busy Boards" where directors sit on too many committees to provide oversight.

### Phase 4: Reporting & HNW Utility

- **US.16:** As a HNW investor, I want a **"One-Page Forensic Tear Sheet"** summarizing the top 3 structural risks found in a new filing.
- **US.17:** As a user, I want to **"Save to Case File"** specific red flags to generate a professional-grade due diligence report for an investment committee.
- **US.18:** As a mobile user, I want an **Active Alert** when a "High-Severity Divergence" (e.g., M-Score breach) is detected in a company I follow.
- **US.19:** As a user, I want to **"Chat with the Auditor"** (LLM) to ask, "Why did you flag this revenue recognition policy?" and receive a cited explanation.
- **US.20:** As an analyst, I want to **Export the Neo4j Relationship Schema** to CSV/Excel to feed into my own proprietary valuation models.

---

## 3. Technical Constraints & Performance

- **Latency:** Full analysis (Ingestion -> Graph Population -> Audit) of a 100-page document must be < 180s.
- **Accuracy:** Use a "Debate Protocol" where two agents (Critic vs. Defender) argue over a red flag to reduce false positives.
- **Traceability:** Every AI claim must have a `Page_Index` and `Paragraph_Hash` metadata tag.

---

###