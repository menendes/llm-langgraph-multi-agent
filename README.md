# Multi‑Agent LLM Threat‑Detection PoC

A minimal yet extensible proof‑of‑concept that shows how a **LangGraph + LLM‑supervised tool‑calling** workflow can detect potential cyber threats from streamed log events.

## Features

| Agent / Tool | Purpose |
|--------------|---------|
| `event_analysis` | Heuristic scoring of every incoming event (rules table, 0‑100) |
| `sql_lookup`     | Counts recent login failures / successes from a local SQLite `logins` table |
| `threat_intel`   | Queries AbuseIPDB for IP reputation (requires free API key) |
| `web_search`     | Context‑aware DuckDuckGo search (IP reputation, attack patterns, CVEs) |
| `notify`         | Sends a Slack alert (or prints to console) when risk is high |

## Architecture

```
stream → main.py  ──► LangGraph supervisor (GPT‑4)
                     │
                     ├─ event_analysis ─┐
                     │                 ├── conditional sql_lookup
                     │                 ├── conditional threat_intel
                     │                 ├── conditional web_search
                     │                 └── optional notify ➜ Slack / stdout
                     ▼
                plain‑English summary
```


## Quick‑start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# environment (optional but recommended)
export OPENAI_API_KEY="<your key>"   # OpenAPI
export ABUSE_IP_DB_KEY="<your key>"  # AbuseIPDB
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."  # Slack
python llm_threat/main.py
```

## Customising

* **Rules** – edit `tools/event_analysis.py` RULES list.
* **DB seed** – modify `_DUMMY` rows in `tools/sql_lookup.py`.
* **Thresholds** – tweak the `SYSTEM_PROMPT` in `driver.py`.
* **Additional tools** – just drop a new callable in `llm_threat/tools/` and add it to `TOOLS`.

## Limitations

* AbuseIPDB calls are live; heavy demos may hit free‑tier rate limits.
* DuckDuckGo search can also rate‑limit; the tool now fails gracefully.
* No persistence between runs except the SQLite file seeded on first launch.

