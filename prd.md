# PRD: Forensic Equity (FE-v1.0)

**Project Code:** "Divergence Engine"

**Target Audience:** Engineering, Forensic Accountants, Institutional Fund Managers

**Core Objective:** To identify the "Say-Do Gap"—the delta between management's qualitative narrative and the quantitative reality of their financial filings.

---

## 0. Executive Summary

Forensic Equity is a specialized financial intelligence platform. It utilizes a **Stateful Multi-Agent System** and **Elasticsearch Hybrid Search** to identify "Narrative Divergence." By combining **BM25 keyword matching** (for specific financial line items) with **kNN dense vector search** (for thematic sentiment), the system detects when management’s story deviates from the hard numbers.

---

## 1. The Forensic Schema: 25 Red Flag Categories

The "Forensic Critic" agent uses these specific patterns to query the Elasticsearch Index, utilizing filtered aggregations and Reciprocal Rank Fusion (RRF) to compare periods.

| # | Category | The "Smoke" (Quant Signal) | The "Mirror" (Qual Narrative) | Logic Trigger |
| --- | --- | --- | --- | --- |
| 1 | Revenue Pull-Forward | DSO↑ while Revenue is flat. | Focus on "Strategic channel wins." | DSO > 1.25× Peer Avg. |
| 2 | Inventory Bloat | Finished Goods ↑ vs. Sales ↓ | "Supply chain resilience prep." | Inventory growth > Sales + 15%. |
| 3 | Expense Shifting | "Other Assets" spike suddenly. | "Investments in efficiency." | Unexplained Asset spike > 5% TA. |
| 4 | Quality of Earnings | Net Income (+) but OCF (-) | "Focus on non-cash growth." | 3 Qtrs of OCF < Net Income. |
| 5 | Margin Compression | COGS as % of Rev ↑ | "Operating leverage" claims. | Margin erosion while claiming "Scale." |
| 6 | Executive Churn | Metadata: CFO/CAO Exit. | "Pursuing personal interests." | Exit within 90 days of 10-K. |
| 7 | Liability Masking | Contingent Liab. text length ↑ | Removal of specific risk keywords. | Textual deletion of known risks. |
| 8 | Capitalized OpEx | PPE/Sales↑ unexpectedly. | "Proprietary tech development." | Shift of OpEx keywords to CapEx. |
| 9 | Goodwill Mirage | Mkt Cap < Book Value. | "Intangible brand strength." | Impairment not taken despite Δ. |
| 10 | Pension Smoothing | Discount rate metadata ↑ | "Prudent actuarial assumptions." | Rate Δ > 50bps vs. Peers. |
| 11 | R&D Capitalization | R&D Exp ↓ while Intangibles ↑ | "Efficiency in R&D pipeline." | Capitalizing > 20% of R&D spend. |
| 12 | Restructuring Addiction | "One-time" charges for 3+ yrs. | "Finalizing the pivot." | Recurring "Non-recurring" items. |
| 13 | Vendor Financing | Accounts Payable ↑ vs. COGS ↔ | "Favorable vendor terms." | AP growth 2× COGS growth. |
| 14 | Lax Credit Quality | Allowance for Doubtful Accts ↓ | "High quality customer mix." | Allowance % ↓ while AR↑. |
| 15 | Related Party Loop | Transactions with "Affiliate" tags. | "Strategic partnerships." | Entities with shared board members. |
| 16 | Tax Strategy Drift | Eff. Tax Rate vs. Statutory Δ↑ | "Jurisdictional optimization." | ETR < 10% without 8-K justification. |
| 17 | Buyback Smoke | Buybacks ↑ while Debt ↑ | "Returning value to shareholders." | Debt-funded share repurchases. |
| 18 | Glossary Drift | Change in "Non-GAAP" definitions. | "Aligning metrics with strategy." | Mathematical formula Δ YoY. |
| 19 | Footnote Obfuscation | Sentence complexity in Footnotes ↑ | "Detailed disclosure." | Gunning Fog Index > 18 in Notes. |
| 20 | Asset Stuffing | "Prepaid Expenses" ↑ vs. OpEx | "Strategic prepayments." | Growth > 3σ from mean. |
| 21 | Audit Fee Squeeze | Audit Fees ↓ while Complexity ↑ | "Focus on cost-efficiency." | Fee ↓ during M&A activity. |
| 22 | Backdated Accruals | Prior period adjustments ↑ | "Standardizing historical data." | Net Income restatements > 2%. |
| 23 | Off-Balance Sheet | Entity nesting depth/count ↑ | "Strategic minority interests." | Total assets in VIE > 10% of Parent. |
| 24 | Linguistic Hedging | Increase in "might," "could," "perhaps." | Vague future outlook. | Hedge-word density ↑ 30% YoY. |
| 25 | Beneish M-Score | Mathematical fraud probability. | High sentiment/Bullish tone. | M-Score > -1.78 + High Sentiment. |

---

## 2. 20 Target User Stories

### Phase 1: Ingestion & Document Indexing

* **US.1:** As a user, I want to upload 10-K/10-Q PDFs to be indexed into **Elasticsearch** as nested documents (Sections > Paragraphs > Sentences) via LlamaParse.
* **US.2:** As an analyst, I want a **"Deep Trace"** feature where I can click a search result and see the original PDF page using the `page_number` metadata stored in the Elasticsearch doc.
* **US.3:** As a developer, I want all financial line items mapped to a **Unified Taxonomy** using Elasticsearch **aliases** and **field mappings** to ensure "Revenue" queries catch "Total Sales."
* **US.4:** As a QA engineer, I want an **"Ingestion Health Report"** that uses Elasticsearch aggregations to verify balance sheet totals match across indexed documents.
* **US.5:** As a user, I want the system to index "Note" references as **Join Fields** (Parent-Child) so I can query a line item and immediately retrieve its corresponding footnote.

### Phase 2: Hybrid Search & Divergence Logic

* **US.6:** As a fund manager, I want a **"Linguistic Drift"** alert by running a **Term Vector** comparison between this year’s "Risk Factors" and last year's.
* **US.7:** As an analyst, I want a **Split-Screen "Reality Check"** view: Hybrid Search retrieves "Management Claims" via Vector similarity and "Financial Reality" via Keyword filters.
* **US.8:** As a user, I want the **"Forensic Critic" (o1 Agent)** to use **Cross-Encoder Re-ranking** on search results to find contradictions between transcripts and filings.
* **US.9:** As an auditor, I want to use **Regex-based search** within Elasticsearch to find "Non-GAAP" adjustments that deviate from standard SEC naming conventions.
* **US.10:** As a user, I want a **"Sentiment-Reality Heatmap"** generated by aggregating sentiment scores (dense vectors) against margin trends (indexed numerical fields).

### Phase 3: Relational Analysis (Non-Graph)

* **US.11:** As a user, I want to search for **"Executive Churn"** by querying an index of "Corporate Events" filtered by company ID and person-name keywords.
* **US.12:** As an analyst, I want to find **"Hidden Peer Risks"** using **More Like This (MLT)** queries to see what risks competitors are disclosing that my target is not.
* **US.13:** As a fund manager, I want to visualize **Subsidiary Complexity** by using Elasticsearch **Nested Aggregations** to see the depth of entity hierarchies.
* **US.14:** As a user, I want to perform a **Global Vector Search** for specific "Accounting Skeletons" (e.g., "Off-balance sheet") across the entire S&P 500 index.
* **US.15:** As an analyst, I want to identify **"Busy Boards"** by running a terms aggregation on Director names to see how many unique Company IDs they are associated with.

### Phase 4: Reporting & HNW Utility

* **US.16:** As a HNW investor, I want a **"One-Page Forensic Tear Sheet"** generated from the top-scored "Divergence" hits in the current search context.
* **US.17:** As a user, I want to **"Tag and Store"** specific Elasticsearch document IDs to a "Case File" index for final report generation.
* **US.18:** As a mobile user, I want an **Active Alert** (Elasticsearch Watcher) triggered when a new filing’s M-Score or Sentiment exceeds a pre-defined threshold.
* **US.19:** As a user, I want to **"Chat with the Auditor"** (LLM) which uses RAG to pull context from the Elasticsearch index and provides citations with `_score` and `source`.
* **US.20:** As an analyst, I want to **Export Search Results** as a flattened CSV/JSON to feed into proprietary valuation models.

---

## 3. Technical Constraints & Performance

* **Search Latency:** Hybrid search (Vector + BM25) + RAG response must be returned in **< 5s** for interactive queries.
* **Indexing Speed:** Full document ingestion and vectorization of a 100-page 10-K must be completed in **< 120s**.
* **Hybrid Weighting:** Utilize **Reciprocal Rank Fusion (RRF)** to balance the weight between keyword matches (exact numbers) and vector matches (vague claims).
* **Traceability:** Every AI claim must include the `doc_id`, `paragraph_offset`, and `version_id` from the Elasticsearch source metadata.

---

## 4. Proposed Elasticsearch Mapping (JSON)

Since we are moving away from Neo4j, our index structure must be highly organized to simulate relationships through nested objects and parent-child joins.

```json
{
  "mappings": {
    "properties": {
      "company_id": { "type": "keyword" },
      "ticker": { "type": "keyword" },
      "filing_type": { "type": "keyword" },
      "period_end_date": { "type": "date" },
      "content_type": { "type": "keyword" }, // e.g., "narrative" vs "financial_table"
      "text_content": { 
        "type": "text", 
        "analyzer": "standard",
        "fields": { "keyword": { "type": "keyword", "ignore_above": 256 } }
      },
      "vector_embedding": { 
        "type": "dense_vector", 
        "dims": 1536, 
        "index": true, 
        "similarity": "cosine" 
      },
      "financial_data": {
        "type": "nested",
        "properties": {
          "label": { "type": "keyword" },
          "value": { "type": "double" },
          "unit": { "type": "keyword" }
        }
      },
      "metadata": {
        "properties": {
          "page_number": { "type": "integer" },
          "sentiment_score": { "type": "float" },
          "is_footnote": { "type": "boolean" }
        }
      }
    }
  }
}


