from datetime import datetime, timezone
received_at = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
print(received_at)