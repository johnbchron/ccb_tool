
import requests, utils, json, secrets
from pprint import pprint

base_path = "https://app.asana.com/api/1.0/"

def main():
	# utils.print_json(list_projects())
	# list_sections_by_project(project_gid=secrets.asana_test_project_gid)
	# utils.print_json(list_sections_by_project(project_gid=secrets.asana_test_project_gid))
	# utils.print_json(list_tasks_by_project(project_gid=secrets.asana_test_project_gid))
	# utils.print_json(list_tasks_by_project(project_gid=secrets.asana_project_gid))
	# utils.print_json(list_subtasks(get_task(str(find_task_by_name("template")), restricted=False)["gid"]))
	# find_task_by_event_id(12345)
	# print(get_master_subtask_names())
	pass

def list_projects():
	headers = {"Authorization": secrets.asana_pat}
	r = requests.get(base_path + "projects", headers=headers)
	# print(r.status_code)
	# utils.print_json(r.json()["data"])
	return r.json()["data"]

def list_sections_by_project(project_gid=secrets.asana_project_gid):
	headers = {"Authorization": secrets.asana_pat}
	r = requests.get(base_path + "projects/" + str(project_gid) + "/sections", headers=headers)
	# print(r.status_code)
	# utils.print_json(r.json()["data"])
	return r.json()["data"]

def list_tasks_by_project(project_gid=secrets.asana_project_gid):
	headers = {"Authorization": secrets.asana_pat}
	r = requests.get(base_path + "projects/" + str(project_gid) + "/tasks", headers=headers)
	# print(r.status_code)
	# utils.print_json(r.json()["data"])
	return r.json()["data"]

def list_subtasks(task_gid):
	headers = {"Authorization": secrets.asana_pat}
	r = requests.get(base_path + "tasks/" + str(task_gid) + "/subtasks", headers=headers)
	# print(r.status_code)
	# utils.print_json(r.json()["data"])
	return r.json()["data"]

def get_master_subtask_names():
	data = list_subtasks(get_task(str(find_task_by_name("template")), restricted=False)["gid"])
	subtask_names = []
	for item in data:
		subtask_names.append(item["name"])
	return subtask_names

def list_tags():
	headers = {"Authorization": secrets.asana_pat}
	r = requests.get(base_path + "tags", headers=headers)
	# print(r.status_code)
	# utils.print_json(r.json()["data"])
	return r.json()["data"]

def find_tag_by_name(name):
	tags = list_tags()
	# print("name of tag to find:", name)
	for tag in tags:
		if name.lower() in tag["name"].lower():
			return int(tag["gid"])
	return None

def get_task(task_gid, restricted=True):
	headers = {"Authorization": secrets.asana_pat}
	params = {}
	if restricted:
		params = {"opt_fields": "name,due_on,html_notes,tags"}
	r = requests.get(base_path + "tasks/" + str(task_gid), headers=headers, params=params)
	# print(r.status_code)
	# utils.print_json(r.json()["data"])
	return r.json()["data"]

def find_task_by_event_id(event_id):
	tasks = list_tasks_by_project()
	tasks = tasks + list_tasks_by_project(project_gid=secrets.asana_test_project_gid)
	# utils.print_json(tasks)
	for task in tasks:
		if ("(" + str(event_id) + ")") in task["name"]:
			# utils.print_json(task)
			return int(task["gid"])
	return None

def find_task_by_name(name):
	tasks = list_tasks_by_project(project_gid=secrets.asana_project_gid)
	for task in tasks:
		if name.lower() in task["name"].lower():
			# utils.print_json(task)
			return int(task["gid"])
	return None

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
	
	payload["data"]["tags"] = []
	if created:
		tag = find_tag_by_name("new")
		if tag is not None:
			payload["data"]["tags"].append(str(tag))
	elif modified:
		tag = find_tag_by_name("updated")
		if tag is not None:
			payload["data"]["tags"].append(str(tag))
	tag = find_tag_by_name(secrets.venue_ids[event["venue"]])
	if tag is not None:
		payload["data"]["tags"].append(str(tag))
	
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

	tags_to_add = []
	if created:
		tag = find_tag_by_name("new")
		if tag is not None:
			tags_to_add.append(str(tag))
	elif modified:
		tag = find_tag_by_name("updated")
		if tag is not None:
			tags_to_add.append(str(tag))
	tag = find_tag_by_name(secrets.venue_ids[event["venue"]])
	if tag is not None:
		tags_to_add.append(str(tag))

	for tag in tags_to_add:
		payload = { "data": { "tag": tag } }
		headers = {"Authorization": secrets.asana_pat}
		r = requests.post(base_path + "tasks/" + str(task_gid) + "/addTag", headers=headers, json=payload)

if __name__ == '__main__':
	main()