from typing import Dict, List, Optional

from duckduckgo_search.exceptions import DuckDuckGoSearchException
from duckduckgo_search import DDGS

ddg = DDGS()

def _run(query: str, n: int) -> List[Dict[str, str]]:
    """Return top *n* results as dicts {title,url,snippet} or empty list on error."""
    try:
        results = ddg.text(query, max_results=n)
        out: List[Dict[str, str]] = []
        for item in results:
            out.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("href", ""),
                    "snippet": item.get("body", ""),
                }
            )
            if len(out) >= n:
                break
        return out
    except DuckDuckGoSearchException as exc:
        print(f"[web_search] rate‑limit: {exc}")
        return []
    except Exception as exc:
        print(f"[web_search] error: {exc}")
        return []

def web_search(
    ip: Optional[str] = None,
    abuse_score: Optional[int] = None,
    threat_signature: Optional[str] = None,
    cve_ids: Optional[List[str]] = None,
    max_results: int = 5,
) -> Dict[str, object]:
    """Run targeted searches and return categorized hit lists."""
    ip_hits: List[str] = []
    pattern_hits: List[str] = []
    cve_hits: Dict[str, List[str]] = {}

    if ip and abuse_score is not None and abuse_score >= 50:
        ip_hits = _run(f"{ip} abuse reports", max_results)

    if threat_signature:
        words = threat_signature.replace("_", " ")
        pattern_hits = _run(f"{words} attack pattern mitigation", max_results)

    if cve_ids:
        for cve in cve_ids[:5]:
            cve_hits[cve] = _run(f"{cve} exploit analysis mitigation", max_results)

    if not (ip_hits or pattern_hits or cve_hits):
        return {"ip_hits": [], "pattern_hits": [], "cve_hits": {}, "error": "no_results_or_query"}

    return {"ip_hits": ip_hits, "pattern_hits": pattern_hits, "cve_hits": cve_hits}