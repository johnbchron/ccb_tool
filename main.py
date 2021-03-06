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

def analyze_recent_events_time_diff(time_diff, catch_errors=True, potent=True, recurring_only=False, one_time_only=False):
	return analyze_recent_event_two_dates(datetime.datetime.now()-time_diff, datetime.datetime.now(), catch_errors=catch_errors, potent=potent, recurring_only=recurring_only, one_time_only=one_time_only)

def analyze_recent_event_two_dates(start_date, end_date, catch_errors=True, potent=True, recurring_only=False, one_time_only=False):

	# declare subtask_names as a global variable
	global subtask_names
	# pull all new events from ccb
	events = ccb.get_recently_modified_events(time_diff=datetime.datetime.now()-start_date)

	# create containers to hold tasks that were created or modified
	# also set time scope for this go-around
	modified_events = []
	created_events = []
	failed_events = []
	last_scan_time = start_date
	this_scan_time = end_date

	print("Concerned with events between", last_scan_time, "and", this_scan_time)

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

	# print("")
	# for event in created_events:
	# 	print(event["name"])
	# print("")
	# for event in modified_events:
	# 	print(event["name"])
	# print("")

	# pull in the subtask names from the template task
	# these subtasks will be added to every new task
	try:
		subtask_names = asana.get_master_subtask_names()
	except:
		print("unable to find subtasks in template. using dummy subtasks instead")
		subtask_names = ["CCBTool was unable to retrieve subtasks", "from the template task.", "This is an error.", "Please contact John Lewis", "at (254) 548-7107 to resolve."]

	# make the checks if the flags say to pass only recurring
	#		or one-time events. remove the non-conformants with extreme prejudice.
	if recurring_only:
		print("only publishing recurring events")
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
		print("after filtering,", len(created_events), "created events and", len(modified_events), "modified events remain")

	elif one_time_only:
		print("only publishing one-time events")
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
		print("after filtering,", len(created_events), "created events and", len(modified_events), "modified events remain")


	# for each created event
	# catch the error if told to do so
	for event in created_events:
		if potent:
			if catch_errors:
				try:
					update_created_event(event)
				except:
					print("failed to create event", event["@id"])
					utils.print_json(event)
					failed_events.append(event)
			else:
				update_created_event(event)
	
	# for each modified event
	# catch the error if told to do so
	for event in modified_events:
		if potent:
			if catch_errors:
				# failed_events.append(event)
				try:
					update_modified_event(event)
				except:
					print("failed to modify event", event["@id"])
					utils.print_json(event)
					failed_events.append(event)
			else:
				update_modified_event(event)

	return failed_events, len(created_events), len(modified_events)


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
