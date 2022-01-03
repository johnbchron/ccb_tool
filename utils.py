
import json, xmltodict, datetime

def parse_datetime(input):
	return datetime.datetime.strptime(input, "%Y-%m-%d %H:%M:%S")

def text_to_json(text):
	return xmltodict.parse(text)

def print_json(data):
	print(json.dumps(data, indent=2))

def uncapitalize(input):
	return input[0].lower() + input[1:]