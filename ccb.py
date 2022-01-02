
import requests, utils, datetime, secrets
from pprint import pprint

base_path = "https://antiochcc.ccbchurch.com/api.php"

def get_recently_modified_events(time_diff=None):
	if time_diff is None:
		time_diff = datetime.timedelta(hours = 4)
	yesterday = str(datetime.date.today() - time_diff - datetime.timedelta(days = 1))
	today = str(datetime.date.today())
	payload = {'srv': 'event_profiles', 'modified_since': yesterday}
	r = requests.get(base_path, params=payload, auth=(secrets.ccb_username, secrets.ccb_password))
	events = []
	
	try:
		event_data = utils.text_to_json(r.text)["ccb_api"]["response"]["events"]["event"]
		if isinstance(event_data, list):
			for event in event_data:
				events.append(event)
		else:
			events.append(event_data)
	except:
		pass
	
	return events