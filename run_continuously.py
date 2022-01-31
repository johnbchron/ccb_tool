
import schedule, time, datetime, json
from main import analyze_recent_events_time_diff
from emailing import send_email

def scheduled_task():
	print("running update at", datetime.datetime.now())
	failed_events, created_count, modified_count = analyze_recent_events_time_diff(datetime.timedelta(hours=24), catch_errors=True)
	
	event_count_string = ""
	if created_count == 1:
		event_count_string += "1 newly created event and "
	else:
		event_count_string += str(created_count) + " newly created events and "
	if modified_count == 1:
		event_count_string += "1 modified event"
	else:
		event_count_string += str(modified_count) + " modified events"

	if not failed_events:
		send_email("CCBTool published all events successfully. Published " + event_count_string + ".")
	else:
		message = "CCBTool found " + event_count_string + ", but failed to publish " + str(len(failed_events)) + " events. Below is the JSON returned by CCB for the failed events:"
		for event in failed_events:
			message += "\n\n" + json.dumps(event, indent=2)
		send_email(message)
	print("finished update at", datetime.datetime.now(), "\n")

# schedule.every(4).hours.do(scheduled_task)
schedule.every().day.at("06:00").do(scheduled_task)

# scheduled_task()
print("ccb_tool started successfully. waiting until next run.")
while True:
  schedule.run_pending()
  time.sleep(60)
