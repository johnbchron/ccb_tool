
import requests, json, datetime, utils, ccb, asana, secrets
from pprint import pprint

time_diff = datetime.timedelta(hours = 72)

def main():
	analyze_recent_events()

def analyze_recent_events():
	events = ccb.get_recently_modified_events()

	modified_events = []
	created_events = []
	this_scan_time = datetime.datetime.now()
	last_scan_time = this_scan_time - time_diff

	for i in range(len(events)):
		if check_for_venue_match(events[i]):
			created = utils.parse_datetime(events[i]["created"])
			modified = utils.parse_datetime(events[i]["modified"])
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

	if isinstance(resources, list):
		for resource in resources:
			if resource["@id"] in secrets.venue_ids:
				event["venue"] = resource["@id"]
				return True
	else:
		if resources["@id"] in secrets.venue_ids:
			event["venue"] = resources["@id"]
			return True

	return False

def update_created_event(event):
	print("pushing created event:", event["@id"])
	task_gid = asana.find_task_by_event_id(int(event["@id"]))
	if task_gid is None:
		asana.create_task_from_event(event, created=True)
	else:
		asana.update_task_from_event(task_gid, event, created=True)

def update_modified_event(event):
	print("updating modified event:", event["@id"])
	task_gid = asana.find_task_by_event_id(int(event["@id"]))
	if task_gid is None:
		asana.create_task_from_event(event, modified=True)
	else:
		asana.update_task_from_event(task_gid, event, modified=True)

if __name__ == '__main__':
	main()