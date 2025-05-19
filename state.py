from typing_extensions import TypedDict

class Event(TypedDict):
    timestamp: str
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str          # e.g. "HTTP", "HTTPS", "SSH"
    http_status: int
    url: str
    method: str            # GET, POST
    user_agent: str        # curl, python, Chrome
    threat_signature: str  # IDS/IPS signature ("" if none)
    bytes_sent: int
    bytes_received: int
    username: str