
import requests, utils, datetime, secrets
from pprint import pprint

base_path = "https://antiochcc.ccbchurch.com/api.php"

# grab all events modified after a certain date from ccb
def get_recently_modified_events(time_diff=None):
	print("collecting recently modified events from ccb...")
	# sets a default for time_diff (4 hours)
	if time_diff is None:
		time_diff = datetime.timedelta(hours = 4)
	#	grab all events from a day before the time specified with time_diff (just for safety)
	yesterday = str(datetime.date.today() - time_diff - datetime.timedelta(days = 1))
	today = str(datetime.date.today())
	payload = {'srv': 'event_profiles', 'modified_since': yesterday}
	r = requests.get(base_path, params=payload, auth=(secrets.ccb_username, secrets.ccb_password))
	events = []
	# allowance for if report only returns one event or no events
	try:
		event_data = utils.text_to_json(r.text)["ccb_api"]["response"]["events"]["event"]
		if isinstance(event_data, list):
			for event in event_data:
				events.append(event)
			print("found", len(events), "events")
		else:
			print("found 1 event")
			events.append(event_data)
	except:
		print("found no events or GET request failed")
	
	return events