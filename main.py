
import requests, json, xmltodict, datetime, secrets
from pprint import pprint

base_path = "https://antiochcc.ccbchurch.com/api.php"
time_diff = datetime.timedelta(hours = 4)

venue_ids = [118, 3, 4, 78, 116, 36, 8, 10, 12]

def main():
	analyze_recent_events()

def analyze_recent_events():
	events = get_recently_modified_events()

	modified_events = []
	created_events = []
	this_scan_time = datetime.datetime.now()
	last_scan_time = this_scan_time - time_diff

	for i in range(len(events)):
		if check_for_venue_match(events[i]):
			print("name:", events[i]["name"])
			created = parse_datetime(events[i]["created"])
			modified = parse_datetime(events[i]["modified"])
			if (created < this_scan_time and created >= last_scan_time):
				created_events.append(events[i])
			elif (modified < this_scan_time and modified >= last_scan_time):
				modified_events.append(events[i])

	for event in created_events:
		update_created_event(event)

	for event in modified_events:
		update_modified_event(event)

def check_for_venue_match(event):
	if event["resources"] is None:
		return False

	resources = event["resources"]["resource"]
	matches_venue = False

	if isinstance(resources, list):
		for resource in resources:
			if int(resource["@id"]) in venue_ids:
				matches_venue = True
	else:
		if int(resources["@id"]) in venue_ids:
			matches_venue = True

	return matches_venue

def update_created_event(event):
	pass

def update_modified_event(event):
	pass

def parse_datetime(input):
	return datetime.datetime.strptime(input, "%Y-%m-%d %H:%M:%S")

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