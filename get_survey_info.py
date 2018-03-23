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
  data = {}
  data[survey_id] = {}
  data[survey_id]["title"] = parsed_data["title"]
  data[survey_id]["question_count"] = parsed_data["question_count"]
  data[survey_id]["response_count"] = parsed_data["response_count"]
  pages = parsed_data["pages"]
  data[survey_id]["pages"] = {}
  for page in pages:
    page_id = page["id"]
    page_position = page["position"] 
    data[survey_id]["pages"][page_id] = {}
    data[survey_id]["pages"][page_id]["position"] = page_position
    data[survey_id]["pages"][page_id]["questions"] = {}
    questions = page["questions"]
    for question in questions:
      question_id = question["id"] 
      question_position = question["position"] 
      data[survey_id]["pages"][page_id]["questions"][question_id] = {}
      data[survey_id]["pages"][page_id]["questions"][question_id]["position"] = question["position"]
  return data

def build_survey_data(surveys):
  survey_data = {}
  for survey in surveys:
    survey_info = get_survey_data(survey["id"])
    survey_data.update(survey_info)
  return survey_data

def write_file(data):
  file = open("survey_data.py","w+")
  file.write("class Survey:\r\n  survey_data = %s" % json.dumps(data, indent=2))
  file.close()

surveys = get_all_surveys()
final_data = build_survey_data(surveys)
write_file(final_data)