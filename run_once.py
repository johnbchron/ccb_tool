
from main import analyze_recent_events_time_diff, analyze_recent_event_two_dates
import datetime
from emailing import send_email

analyze_recent_events_time_diff(datetime.timedelta(hours=4), catch_errors=False)
# analyze_recent_event_two_dates(datetime.datetime(2021,6,2,6,0,0), datetime.datetime(2021,12,2,6,0,0), catch_errors=False, recurring_only=True)
# send_email("This is a test email. It worked")