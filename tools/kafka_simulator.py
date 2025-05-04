# tools/kafka_simulator.py
def get_sample_events():
    return [
        {
            "timestamp": "2025-05-01T08:15:00",
            "ip_address": "192.168.1.15",
            "event_type": "login",
            "success": False,
            "username": "alice",
            "source": "auth"
        },
        # {
        #     "timestamp": "2025-04-01T10:15:00",
        #     "ip_address": "192.168.1.11",
        #     "event_type": "login",
        #     "success": True,
        #     "username": "bob",
        #     "source": "auth"
        # },
        # {
        #     "timestamp": "2025-04-01T10:20:00",
        #     "ip_address": "203.0.113.50",
        #     "event_type": "login",
        #     "success": False,
        #     "username": "charlie",
        #     "source": "vpn"
        # },
        # {
        #     "timestamp": "2025-04-02T09:00:00",
        #     "ip_address": "198.51.100.25",
        #     "event_type": "password_reset",
        #     "success": True,
        #     "username": "diana",
        #     "source": "web"
        # }
    ]
