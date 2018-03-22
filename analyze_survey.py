# what would be valuable is to track results on the areas of the event 
# (i.e. reg, hotel, networking, etc) against previous survey results 
# by brand - possible?

import requests
import math
from surveymonkey_keys import Key

s = requests.Session()
s.headers.update({
  "Authorization": "Bearer %s" % Key.access_token,
  "Content-Type": "application/json"
})

survey_ids = [130576734]

def how_many_pages(survey_id):
  url = "https://api.surveymonkey.com/v3/surveys/%s/responses/" % (survey_id)
  parameters = {
    "per_page": "100"
  }
  parsed_data = s.get(url, params=parameters).json()
  print (parsed_data)
  number_pages = math.ceil(parsed_data["total"]/100)
  return number_pages

def get_all_responses(survey_id, pages):
  responses = []
  for n in range(pages):
    url = "https://api.surveymonkey.com/v3/surveys/%s/responses/bulk/" % (survey_id)
    parameters = {
      "per_page": "100",
      "page": n+1
    }
    parsed_data = s.get(url, params=parameters).json()
    page_responses = parsed_data["data"]
    responses += (page_responses.copy())
  return responses

def get_survey_data(survey_id):
  url = "https://api.surveymonkey.com/v3/surveys/%s/details/" % (survey_id)
  parsed_data = s.get(url).json()
  question_count = parsed_data["question_count"]
  response_count = parsed_data["response_count"]
  pages = parsed_data["pages"]
  for page in pages:
    questions = page["questions"]
    print (questions)  
  print (question_count)
  print (response_count)

  # number_questions = math.ceil(parsed_data["total"]/100)
  # return number_questions

# def get_all_questions(survey_id, pages):
#   url = "https://api.surveymonkey.com/v3/surveys/%s/pages/1/questions" % (survey_id, page_id)
#   parameters = {
#     "per_page": "100",
#   }



for survey_id in survey_ids:
  questions = get_survey_data(survey_id)
  # pages = how_many_pages(survey_id)
  # responses = get_all_responses(survey_id, pages)
  