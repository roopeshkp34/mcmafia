import asyncio
from app.services.enrichment import enrichment_service

async def test_enrichment():
    ticker = enrichment_service.extract_ticker("AAPL_2023_10K.pdf")
    print(f"Extracted Ticker: {ticker}")
    assert ticker == "AAPL"
    
    # Test LLM Identification
    sample_text = "Apple Inc. today announced its 2023 financial results..."
    company_name = await enrichment_service.identify_company(sample_text)
    print(f"Identified Company: {company_name}")
    assert "Apple" in company_name
    
    # Test Tavily Enrichment
    enrichment = await enrichment_service.fetch_tavily_enrichment(company_name)
    print(f"Tavily Enrichment: {enrichment}")
    assert "company_overview" in enrichment or "about" in enrichment
    
    metadata = {"page": 1}
    enriched = enrichment_service.enrich_page("This is a risk factor with $1 million revenue.", metadata)
    print(f"Enriched Metadata: {enriched}")
    assert len(enriched["highlights"]) == 3
    print("Enrichment tests passed!")

if __name__ == "__main__":
    asyncio.run(test_enrichment())
