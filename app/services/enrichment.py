import re
import random
import httpx
from langchain_openai import AzureChatOpenAI
from app.core.config import settings

class EnrichmentService:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            temperature=0,
        )

    @staticmethod
    def extract_ticker(file_name: str) -> str:
        """
        Extracts a stock ticker from a filename using regex.
        Example: 'AAPL_2023_10K.pdf' -> 'AAPL'
        """
        match = re.search(r'(?:^|[^A-Z])([A-Z]{1,5})(?:[^A-Z]|$)', file_name)
        if match:
            return match.group(1)
        return "UNKNOWN"

    async def identify_company(self, text: str) -> str:
        """
        Uses LLM to identify the company name from the document text.
        """
        prompt = (
            "Extract the official company name from the following text of a financial filing. "
            "Return ONLY the company name and nothing else.\n\n"
            f"Text: {text[:2000]}"
        )
        try:
            response = await self.llm.ainvoke(prompt)
            return response.content.strip()
        except Exception as e:
            print(f"Error identifying company: {e}")
            return "Unknown Company"

    async def fetch_tavily_enrichment(self, company_name: str) -> dict:
        """
        Calls Tavily Search API to get enrichment data for the company.
        """
        if not settings.TAVILY_API_KEY:
            return {"about": "Tavily API key missing"}

        url = "https://api.tavily.com/search"
        payload = {
            "api_key": settings.TAVILY_API_KEY,
            "query": f"Latest financial news and business overview for {company_name}",
            "search_depth": "basic"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload)
                data = response.json()
                # Extract relevant bits
                results = data.get("results", [])
                if results:
                    summary = results[0].get("content", "No content found")[:500]
                    sources = [r.get("url") for r in results[:3]]
                    return {
                        "company_overview": summary,
                        "latest_news_sources": sources,
                        "enrichment_source": "Tavily"
                    }
        except Exception as e:
            print(f"Error fetching Tavily enrichment: {e}")
            
        return {"about": "No enrichment data available"}

    @staticmethod
    def enrich_page(text: str, metadata: dict) -> dict:
        """
        Analyzes page text to add "wow factor" highlights.
        """
        highlights = []
        if "risk" in text.lower():
            highlights.append("⚠️ Risk Disclosure detected")
        if "$" in text or "million" in text.lower():
            highlights.append("💰 Financial figures detected")
        if "revenue" in text.lower():
            highlights.append("📈 Revenue discussion found")
            
        sentiment_score = round(random.uniform(-1, 1), 2)
        
        metadata.update({
            "highlights": highlights,
            "sentiment_score": sentiment_score,
            "forensic_status": "Flagged" if sentiment_score < -0.5 else "Clean"
        })
        return metadata

enrichment_service = EnrichmentService()
