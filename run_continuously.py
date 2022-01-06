
import schedule, time, datetime, json
from main import analyze_recent_events_time_diff
from emailing import send_email

def scheduled_task():
	print("running update at", datetime.datetime.now())
	failed_events = analyze_recent_events_time_diff(datetime.timedelta(hours=24), catch_errors=True)
	print("finished update at", datetime.datetime.now(), "\n")
	if not failed_events:
		send_email("All events published successfully. No errors occured.")
	else:
		message = "CCBTool failed to publish " + str(len(failed_events)) + " events. Below is the JSON returned by CCB for the failed events:"
		for event in failed_events:
			message += "\n\n" + json.dumps(event, indent=2)
		send_email(message)

# schedule.every(4).hours.do(scheduled_task)
schedule.every().day.at("06:00").do(scheduled_task)

# scheduled_task()
while True:
  schedule.run_pending()
  time.sleep(60)
