
import requests, utils, json, secrets
from pprint import pprint

base_path = "https://app.asana.com/api/1.0/"

def main():
	# utils.print_json(list_projects())
	# list_sections_by_project(project_gid=secrets.asana_test_project_gid)
	utils.print_json(list_sections_by_project(project_gid=secrets.asana_test_project_gid))
	# list_tasks_by_project(project_gid=secrets.asana_test_project_gid)
	# list_tasks_by_project(project_gid=secrets.asana_project_gid)
	# get_task(str(1201548447662435))
	# find_task_by_event_id(12345)

def list_projects():
	headers = {"Authorization": secrets.asana_pat}
	r = requests.get(base_path + "projects", headers=headers)
	# print(r.status_code)
	# utils.print_json(r.json()["data"])
	return r.json()["data"]

def list_sections_by_project(project_gid=secrets.asana_project_gid):
	headers = {"Authorization": secrets.asana_pat}
	r = requests.get(base_path + "projects/" + project_gid + "/sections", headers=headers)
	# print(r.status_code)
	# utils.print_json(r.json()["data"])
	return r.json()["data"]

def list_tasks_by_project(project_gid=secrets.asana_project_gid):
	headers = {"Authorization": secrets.asana_pat}
	r = requests.get(base_path + "projects/" + project_gid + "/tasks", headers=headers)
	# print(r.status_code)
	# utils.print_json(r.json()["data"])
	return r.json()["data"]

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

def get_task(task_gid):
	headers = {"Authorization": secrets.asana_pat}
	r = requests.get(base_path + "tasks" + task_gid, headers=headers)
	# print(r.status_code)
	# utils.print_json(r.json()["data"])
	return r.json()["data"]

def find_task_by_event_id(event_id):
	tasks = list_tasks_by_project()
	tasks = tasks + list_tasks_by_project(project_gid=secrets.asana_test_project_gid)
	# utils.print_json(tasks)
	for task in tasks:
		if ("(" + str(event_id) + ")") in task["name"]:
			utils.print_json(task)
			return int(task["gid"])
	return None

def create_task_from_event(event, created=False, modified=False):
	# utils.print_json(event)
	payload = { "data": {} }
	payload["data"]["projects"] = [secrets.asana_test_project_gid]
	payload["data"]["due_on"] = event["start_datetime"][:10]
	pretty_date = str(int(event["start_datetime"][5:7])) + "/" + str(int(event["start_datetime"][8:10]))
	payload["data"]["name"] = pretty_date + " " + event["name"] + " (" + str(event["@id"]) + ")"
	payload["data"]["html_notes"] = "<body><ul><li><a href=\"https://antiochcc.ccbchurch.com/event_detail.php?event_id=" + str(event["@id"]) + "\">CCB</a></li></ul></body>"
	if created:
		tag = find_tag_by_name("new")
		if tag is not None:
			payload["data"]["tags"] = [str(tag)]
	elif modified:
		tag = find_tag_by_name("changed/updated")
		if tag is not None:
			payload["data"]["tags"] = [str(tag)]
	tag = find_tag_by_name(secrets.venue_ids[event["venue"]])
	if tag is not None:
		payload["data"]["tags"].append(str(tag))
	utils.print_json(payload)

	headers = {"Authorization": secrets.asana_pat}
	r = requests.post(base_path + "tasks", headers=headers, json=payload)

	task_gid = r.json()["data"]["gid"]

	payload = { "data": { "task": task_gid} }

	headers = {"Authorization": secrets.asana_pat}
	if "every" in event["recurrence_description"].lower():
		r = requests.post(base_path + "sections/" + secrets.asana_test_recurring_section_gid + "/addTask", headers=headers, json=payload)
	else:
		r = requests.post(base_path + "sections/" + secrets.asana_test_one_time_section_gid + "/addTask", headers=headers, json=payload)

def update_task_from_event(task_gid, event, created=False, modified=False):
	pass

if __name__ == '__main__':
	main()