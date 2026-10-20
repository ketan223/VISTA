import os
import requests
from bs4 import BeautifulSoup
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()

@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic. Returns Titles, URLs and snippets."""
    # 1. Try Tavily Search first if API key is configured
    api_key = os.getenv("TAVILY_API_KEY", "").strip()
    if api_key:
        try:
            from tavily import TavilyClient
            tavily = TavilyClient(api_key=api_key)
            results = tavily.search(query=query, max_results=5)
            out = []
            for r in results.get("results", []):
                out.append(
                    f"Title: {r.get('title', 'No Title')}\nURL: {r.get('url', '')}\nSnippet: {r.get('content', '')[:300]}\n"
                )
            if out:
                return "\n----\n".join(out)
        except Exception as e:
            # Plan exceeded or rate limit - seamlessly fallback
            pass

    # 2. Resilient fallback: DuckDuckGo Search (DDGS)
    try:
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS
        
        results = list(DDGS().text(query, max_results=5))
        out = []
        for r in results:
            out.append(
                f"Title: {r.get('title', 'No Title')}\nURL: {r.get('href', '')}\nSnippet: {r.get('body', '')[:300]}\n"
            )
        if out:
            return "\n----\n".join(out)
    except Exception as e:
        return f"Search encountered an error: {str(e)}"

    return "No search results found for the requested topic."


@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    try:
        resp = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        
        paragraphs = soup.find_all(["p", "h1", "h2", "h3", "li"])
        if paragraphs:
            text = " ".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        else:
            text = soup.get_text(separator=" ", strip=True)
            
        clean_text = " ".join(text.split())
        return clean_text[:3000] if clean_text else "No readable text content found on the page."
    except Exception as e:
        return f"Could not scrape URL {url}: {str(e)}"
