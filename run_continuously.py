
import schedule, time, datetime
from main import analyze_recent_events

def scheduled_task():
	print("running update at", datetime.datetime.now())
	analyze_recent_events(catch_errors=True)
	print("finished update at", datetime.datetime.now(), "\n")

schedule.every(4).hours.do(scheduled_task)

scheduled_task()
while True:
    schedule.run_pending()
    time.sleep(60)