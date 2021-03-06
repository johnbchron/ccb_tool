
import requests, utils, json, secrets
from pprint import pprint

base_path = "https://app.asana.com/api/1.0/"

def main():
	# don't run any tests
	pass

# list all projects in antioch workspace
def list_projects():
	headers = {"Authorization": secrets.asana_pat}
	r = requests.get(base_path + "projects", headers=headers)
	# print(r.status_code)
	# utils.print_json(r.json()["data"])
	return r.json()["data"]

# list all sections within a project
def list_sections_by_project(project_gid=secrets.asana_test_project_gid):
	headers = {"Authorization": secrets.asana_pat}
	r = requests.get(base_path + "projects/" + str(project_gid) + "/sections", headers=headers)
	# print(r.status_code)
	# utils.print_json(r.json()["data"])
	return r.json()["data"]

# list all tasks within a project
def list_tasks_by_project(project_gid=secrets.asana_test_project_gid):
	headers = {"Authorization": secrets.asana_pat}
	r = requests.get(base_path + "projects/" + str(project_gid) + "/tasks", headers=headers)
	# print(r.status_code)
	# utils.print_json(r.json()["data"])
	return r.json()["data"]

# list all subtasks within a task
def list_subtasks(task_gid):
	headers = {"Authorization": secrets.asana_pat}
	r = requests.get(base_path + "tasks/" + str(task_gid) + "/subtasks", headers=headers)
	# print(r.status_code)
	# utils.print_json(r.json()["data"])
	return r.json()["data"]

# return array of names of subtasks from the template task in the test project
def get_master_subtask_names():
	task = find_task_by_name("template", project_gid=secrets.asana_test_project_gid)
	data = list_subtasks(get_task(str(task), restricted=False)["gid"])
	subtask_names = []
	for item in data:
		subtask_names.append(item["name"])
	# print(subtask_names[::-1])
	return subtask_names[::-1]

# list all tags in antioch workspace
def list_tags():
	headers = {"Authorization": secrets.asana_pat}
	r = requests.get(base_path + "tags", headers=headers)
	# print(r.status_code)
	# utils.print_json(r.json()["data"])
	return r.json()["data"]

# find a tag that matches the given name inside the antioch workspace
def find_tag_by_name(name):
	tags = list_tags()
	# print("name of tag to find:", name)
	for tag in tags:
		if name.lower() in tag["name"].lower():
			return int(tag["gid"])
	return None

# return all or specific fields from the task at the given id
def get_task(task_gid, restricted=True):
	headers = {"Authorization": secrets.asana_pat}
	params = {}
	if restricted:
		params = {"opt_fields": "name,due_on,html_notes,tags"}
	r = requests.get(base_path + "tasks/" + str(task_gid), headers=headers, params=params)
	# print(r.status_code)
	# utils.print_json(r.json()["data"])
	return r.json()["data"]

# find the task that corresponds to the given event id
def find_task_by_event_id(event_id):
	tasks = list_tasks_by_project(project_gid=secrets.asana_test_project_gid)
	# utils.print_json(tasks)
	for task in tasks:
		if ("(" + str(event_id) + ")") in task["name"]:
			# utils.print_json(task)
			return int(task["gid"])
	return None

# find the task that matches the given name (used for finding the template task)
def find_task_by_name(name, project_gid=secrets.asana_test_project_gid):
	tasks = list_tasks_by_project(project_gid=project_gid)
	for task in tasks:
		if name.lower() in task["name"].lower():
			# utils.print_json(task)
			return int(task["gid"])
	return None

# generates the task description containing the event link, recurrance description, and exceptions
def generate_task_description(event):
	recurring = False
	if "every" in event["recurrence_description"].lower():
		recurring = True

	html_string = "<body>"
	html_string += "<a href=\"https://antiochcc.ccbchurch.com/event_detail.php?event_id=" + str(event["@id"]) + "\">CCB Event</a>\n"
	if recurring:
		html_string += "Event occurs " + utils.uncapitalize(event["recurrence_description"]) + "\n"
		if event["exceptions"] is not None:
			html_string += "Exceptions:<ul>"
			if isinstance(event["exceptions"]["exception"], list):
				for exception in event["exceptions"]["exception"]:
					html_string += "<li>" + exception["date"] + "</li>"
			else:
				html_string += "<li>" + event["exceptions"]["exception"]["date"] + "</li>"
			html_string += "</ul>"
	html_string += "<strong>--- don't edit above this line ---</strong>\n"
	html_string += "</body>"

	return html_string

# builds and posts a task based on a ccb event
def create_task_from_event(event, subtask_names, created=False, modified=False):
	# utils.print_json(event)

	recurring = False
	if "every" in event["recurrence_description"].lower():
		recurring = True
	
	payload = { "data": {} }
	payload["data"]["projects"] = [secrets.asana_test_project_gid]
	payload["data"]["due_on"] = event["start_datetime"][:10]
	pretty_date = str(int(event["start_datetime"][5:7])) + "/" + str(int(event["start_datetime"][8:10]))
	payload["data"]["name"] = pretty_date + " " + event["name"] + " (" + str(event["@id"]) + ")"
	
	payload["data"]["html_notes"] = generate_task_description(event)
	
	payload["data"]["tags"] = list_relevant_tags(event, created, modified)
	
	# utils.print_json(payload)

	headers = {"Authorization": secrets.asana_pat}
	r = requests.post(base_path + "tasks", headers=headers, json=payload)
	# utils.print_json(r.json())

	task_gid = r.json()["data"]["gid"]

	payload = { "data": { "task": task_gid} }
	if recurring:
		r = requests.post(base_path + "sections/" + secrets.asana_test_recurring_section_gid + "/addTask", headers=headers, json=payload)
	else:
		r = requests.post(base_path + "sections/" + secrets.asana_test_one_time_section_gid + "/addTask", headers=headers, json=payload)

	for subtask_name in subtask_names:
		payload = { "data": { "name": subtask_name } }
		r = requests.post(base_path + "tasks/" + str(task_gid) + "/subtasks", headers=headers, json=payload)

# builds and updates an event based on a ccb event
def update_task_from_event(task_gid, event, created=False, modified=False):
	trigger_text = "<strong>--- don't edit above this line ---</strong>\n"

	task = get_task(task_gid)
	# utils.print_json(task)

	recurring = False
	if "every" in event["recurrence_description"].lower():
		recurring = True

	payload = { "data": {} }
	payload["data"]["due_on"] = event["start_datetime"][:10]
	pretty_date = str(int(event["start_datetime"][5:7])) + "/" + str(int(event["start_datetime"][8:10]))
	payload["data"]["name"] = pretty_date + " " + event["name"] + " (" + str(event["@id"]) + ")"

	try:
		task["html_notes"] = task["html_notes"][task["html_notes"].index(trigger_text) + len(trigger_text):-7]
		task["html_notes"] = generate_task_description(event)[:-7] + task["html_notes"] + "</body>"
		# print(task["html_notes"])
	except:
		# print("could not find trigger text")
		task["html_notes"] = generate_task_description(event) + task["html_notes"]

	headers = {"Authorization": secrets.asana_pat}
	r = requests.put(base_path + "tasks/" + str(task_gid), headers=headers, json=payload)

	for tag in task["tags"]:
		payload = { "data": { "tag": tag["gid"] } }
		headers = {"Authorization": secrets.asana_pat}
		r = requests.post(base_path + "tasks/" + str(task_gid) + "/removeTag", headers=headers, json=payload)

	tags_to_add = list_relevant_tags(event, created, modified)
	for tag in tags_to_add:
		payload = { "data": { "tag": tag } }
		headers = {"Authorization": secrets.asana_pat}
		r = requests.post(base_path + "tasks/" + str(task_gid) + "/addTag", headers=headers, json=payload)

def list_relevant_tags(event, created, modified):
	# every time a tag is proposed, the function looks for it
	# if the tag is found, it's added, otherwise it isn't

	# if the event should have the new tag, add it
	tags_to_add = []
	if created:
		tag = find_tag_by_name("new")
		if tag is not None:
			tags_to_add.append(str(tag))
	# if the event is not new and should have the modified tag, add it
	elif modified:
		tag = find_tag_by_name("updated")
		if tag is not None:
			tags_to_add.append(str(tag))

	resources = event["resources"]["resource"]
	# because the data starts as xml, if what would be an array in json
	# 	only has one element, it isn't converted to json, so this checks for that
	if isinstance(resources, list):
		for resource in resources:
			if resource["@id"] in secrets.venue_ids:
				tag = find_tag_by_name(secrets.venue_ids[resource["@id"]])
				if tag is not None:
					tags_to_add.append(str(tag))
	else:
		if resources["@id"] in secrets.venue_ids:
			tag = find_tag_by_name(secrets.venue_ids[resources["@id"]])
			if tag is not None:
				tags_to_add.append(str(tag))

	return tags_to_add

# if this file is run, run the test method
if __name__ == '__main__':
	main()