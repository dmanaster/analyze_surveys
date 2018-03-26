import requests
import json
from surveymonkey_keys import Key

s = requests.Session()
s.headers.update({
  "Authorization": "Bearer %s" % Key.access_token,
  "Content-Type": "application/json"
})

def get_all_surveys():
  url = "https://api.surveymonkey.com/v3/surveys"
  parameters = {
    "per_page": "200"
  }
  parsed_data = s.get(url, params=parameters).json()
  surveys = parsed_data["data"]
  survey_data = []
  for survey in surveys:
    data = {}
    data["title"] = survey["title"]
    data["id"] = survey["id"]
    survey_data.append(data.copy())
  return survey_data

def get_survey_data(survey_id):
  url = "https://api.surveymonkey.com/v3/surveys/%s/details/" % (survey_id)
  parsed_data = s.get(url).json()
  survey_id = parsed_data["id"]
  data = parsed_data
  return data

def build_survey_data(surveys):
  survey_data = []
  for survey in surveys:
    survey_info = get_survey_data(survey["id"])
    survey_data.append(survey_info.copy())
  return survey_data

def write_file(data):
  file = open("survey_data.py","w+")
  file.write("class Survey:\r\n  survey_data = %s" % json.dumps(data, indent=2))
  file.close()

def clean_file():
  with open('survey_data.py', 'r') as file :
    filedata = file.read()
  filedata = filedata.replace('true', 'True')
  filedata = filedata.replace('false', 'False')
  filedata = filedata.replace('null', 'None')
  with open('survey_data.py', 'w') as file:
    file.write(filedata)

surveys = get_all_surveys()
final_data = build_survey_data(surveys)
write_file(final_data)
clean_file()