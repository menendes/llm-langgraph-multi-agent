import os, requests, textwrap, json
from typing import Dict, List, Optional

WEBHOOK = os.getenv("SLACK_WEBHOOK_URL", "")

def notify(summary: str, risk: int, src_ip: str, links: Optional[List[str]] = None) -> Dict[str, str]:
    """Send Slack alert (if WEBHOOK set) or print to console."""
    text = textwrap.dedent(
        f"""
        *THREAT ALERT*  (risk {risk}/100)
        Source IP: {src_ip}

        {summary}
        {"References:" + "• ".join(links[:3]) if links else ""}
        """
    )
    if not WEBHOOK:
        print("[notify]", text)
        return {"status": "printed"}
    try:
        requests.post(WEBHOOK, json={"text": text}).raise_for_status()
        return {"status": "sent"}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}