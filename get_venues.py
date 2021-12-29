
import requests, json, xmltodict, datetime, secrets
from pprint import pprint

base_path = "https://antiochcc.ccbchurch.com/api.php"

def main():
	payload = {'srv': 'resource_list'}
	r = requests.get(base_path, params=payload, auth=(secrets.username, secrets.password))
	response = text_to_json(r.text)["ccb_api"]["response"]
	print_json(response)

def text_to_json(text):
	return xmltodict.parse(text)

def print_json(data):
	print(json.dumps(data, indent=2))

if __name__ == '__main__':
	main()