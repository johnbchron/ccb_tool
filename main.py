import sys

sys.path.insert(0, './config/')

import requests, json, datetime, utils, ccb, asana, secrets
from pprint import pprint

#time_diff = datetime.timedelta(hours = 4)

catch_errors = True
subtask_names = []

def main():
	# analyze_recent_events()
	pass

def analyze_recent_events(catch_errors=True, recurring_only=False, one_time_only=False, time_diff=datetime.timedelta(hours=4)):
	# declare subtask_names as a global variable
	global subtask_names
	# pull all new events from ccb
	events = ccb.get_recently_modified_events(time_diff=time_diff)

	# create containers to hold tasks that were created or modified
	# also set time scope for this go-around
	modified_events = []
	created_events = []
	this_scan_time = datetime.datetime.now()
	last_scan_time = this_scan_time - time_diff

	print("Concerned with events between", last_scan_time, "and now")

	# for every event, first check if it matches one of the venues
	# then parse out its creation and modified times
	# then sort it if it matches its creation or modification time falls in the window
	for i in range(len(events)):
		if check_for_venue_match(events[i]):
			created = utils.parse_datetime(events[i]["created"])
			modified = utils.parse_datetime(events[i]["modified"])
			if (created < this_scan_time and created >= last_scan_time):
				created_events.append(events[i])
			elif (modified < this_scan_time and modified >= last_scan_time):
				modified_events.append(events[i])

	print("out of", len(events), "events,", len(created_events), "were created and", len(modified_events), "were modified within the timeframe")

	# pull in the subtask names from the template task
	# these subtasks will be added to every new task
	subtask_names = asana.get_master_subtask_names()

	# make the checks if the flags say to pass only recurring
	#		or one-time events. remove the non-conformants with extreme prejudice.
	if recurring_only:
		passing_items = []
		for i in range(len(created_events)):
			if check_if_recurring(created_events[i]):
				passing_items.append(created_events[i])
		created_events = passing_items

		passing_items = []
		for i in range(len(modified_events)):
			if check_if_recurring(modified_events[i]):
				passing_items.append(modified_events[i])
		modified_events = passing_items

	elif one_time_only:
		passing_items = []
		for i in range(len(created_events)):
			if not check_if_recurring(created_events[i]):
				passing_items.append(created_events[i])
		created_events = passing_items

		passing_items = []
		for i in range(len(modified_events)):
			if not check_if_recurring(modified_events[i]):
				passing_items.append(modified_events[i])
		modified_events = passing_items


	# for each created event
	# catch the error if told to do so
	for event in created_events:
		if catch_errors:
			try:
				update_created_event(event)
			except:
				print("failed to create event", event["@id"])
				utils.print_json(event)
		else:
			update_created_event(event)
	
	# for each modified event
	# catch the error if told to do so
	for event in modified_events:
		if catch_errors:
			try:
				update_modified_event(event)
			except:
				print("failed to modify event", event["@id"])
				utils.print_json(event)
		else:
			update_modified_event(event)

# checks if the event carries a resource that matches one of the specified venues
# these venues are specified in the secrets file
def check_for_venue_match(event):
	# fail if the event doesn't have any resources
	if event["resources"] is None:
		return False
	resources = event["resources"]["resource"]

	# because the data starts as xml, if what would be an array in json
	# 	only has one element, it isn't converted to json, so this checks for that
	if isinstance(resources, list):
		for resource in resources:
			if resource["@id"] in secrets.venue_ids:
				event["venue"] = resource["@id"]
				return True
	else:
		if resources["@id"] in secrets.venue_ids:
			event["venue"] = resources["@id"]
			return True
	# fail otherwise
	return False

# check if the event is a recurring event
# currently the only way to do this is to check whether or not
# 	the word "every" is in the recurrence description
def check_if_recurring(event):
	recurring = False
	if "every" in event["recurrence_description"].lower():
		recurring = True
	return recurring

#	if the task exists, modify it, otherwise create it
# also add created tag
def update_created_event(event):
	global subtask_names
	print("pushing created event:", event["@id"])
	task_gid = asana.find_task_by_event_id(int(event["@id"]))
	if task_gid is None:
		asana.create_task_from_event(event, subtask_names, created=True)
	else:
		asana.update_task_from_event(task_gid, event, created=True)

#	if the task exists, modify it, otherwise create it
# also add modified tag
def update_modified_event(event):
	global subtask_names
	print("updating modified event:", event["@id"])
	task_gid = asana.find_task_by_event_id(int(event["@id"]))
	if task_gid is None:
		asana.create_task_from_event(event, subtask_names, modified=True)
	else:
		asana.update_task_from_event(task_gid, event, modified=True)

if __name__ == '__main__':
	main()
