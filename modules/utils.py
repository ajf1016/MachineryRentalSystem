from datetime import datetime
import pytz


def format_time_to_ist(timestamp):
    """Converts a UTC timestamp to Indian Standard Time (IST) and formats it in 12-hour format."""
    if not timestamp:
        return "N/A"
    # Assuming the database stores time in this format
    utc_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    ist_time = utc_time.replace(tzinfo=pytz.UTC).astimezone(
        pytz.timezone("Asia/Kolkata"))
    # Shortened format: YYYY-MM-DD HH:MM AM/PM
    return ist_time.strftime("%Y-%m-%d %I:%M %p")
