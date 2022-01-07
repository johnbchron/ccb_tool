
from main import analyze_recent_events_time_diff, analyze_recent_event_two_dates
import datetime
from emailing import send_email

# analyze_recent_events_time_diff(datetime.timedelta(hours=4), catch_errors=False)
analyze_recent_event_two_dates(datetime.datetime(2021,11,22,6,0,0), datetime.datetime(2021,12,3,6,0,0), catch_errors=False)
# send_email("This is a test email. It worked")