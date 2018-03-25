import requests
import json
from surveymonkey_keys import Key
from survey_data import Survey
from target_questions import Target
import math

s = requests.Session()
s.headers.update({
  "Authorization": "Bearer %s" % Key.access_token,
  "Content-Type": "application/json"
})

responses = {}

def get_survey_responses(survey_id, pages):
  responses[survey_id] = {}
  for n in range(pages):
    url = "https://api.surveymonkey.com/v3/surveys/%s/responses/bulk/" % (survey_id)
    parameters = {
      "per_page": "100",
      "page": n+1
    }
    parsed_data = s.get(url, params=parameters).json()
    page_responses = parsed_data["data"]
    for response in page_responses:
      response_id = response["id"]
      responses[survey_id][response_id] = response
  return responses

def get_survey(survey_id):
  survey = Survey.survey_data[survey_id]
  return survey

def get_pages(survey):
  pages = math.ceil(survey["response_count"]/100)
  return pages

def write_file(data):
  file = open("response_data.py","w+")
  file.write("class Response:\r\n  response_data = %s" % json.dumps(data, indent=2))
  file.close()


for key in Target.target_info:
  pages = get_pages(get_survey(key))
  survey_responses = get_survey_responses(key, pages)
  write_file(survey_responses)