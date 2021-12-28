
import requests, json, xmltodict, datetime, secrets
from pprint import pprint

base_path = "https://antiochcc.ccbchurch.com/api.php"
time_diff = datetime.timedelta(hours = 4)

def main():
	analyze_recent_events()

def analyze_recent_events():
	events = get_recently_modified_events()
	modified_events = []
	created_events = []
	# for i in range(len(events)):
	# 	created_time = events[i]["created"]
	# 	if (events[i]

def retrieve_event_created_time():
	pass

def get_recently_modified_events():
	yesterday = str(datetime.date.today() - datetime.timedelta(days = 10))
	today = str(datetime.date.today())
	payload = {'srv': 'event_profiles', 'modified_since': yesterday}
	print("searching for events modified between", yesterday, "and", today)
	r = requests.get(base_path, params=payload, auth=(secrets.username, secrets.password))
	events = []
	
	try:
		event_data = text_to_json(r.text)["ccb_api"]["response"]["events"]["event"]
		for event in event_data:
			events.append(event)
	except:
		pass
	
	print("found", len(events), "events in the timeframe")
	return events

def text_to_json(text):
	return xmltodict.parse(text)

def print_json(data):
	print(json.dumps(data, indent=2))



if __name__ == '__main__':
	main()