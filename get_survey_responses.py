from surveymonkey_keys import Key
from survey_data import Survey
import math

survey_ids = ['130576734']

def get_survey_responses(survey_id, pages):
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

def get_survey(survey_id):
  survey = Survey.survey_data[survey_id]
  return survey

def get_pages(survey):
  pages = math.ceil(survey["response_count"]/100)
  return pages

for survey_id in survey_ids:
  pages = get_pages(get_survey(survey_id))
  get_survey_responses(survey_id, pages)
