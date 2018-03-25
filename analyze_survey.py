# what would be valuable is to track results on the areas of the event 
# (i.e. reg, hotel, networking, etc) against previous survey results 
# by brand - possible?

from target_questions import Target
from survey_data import Survey
from response_data import Response

survey_data = Survey.survey_data
target_surveys = Target.target_info
response_data = Response.response_data

def get_nps_question(target_surveys):
  for survey_id, data in target_surveys.items():
    target_questions = data["questions"]
    page_id = target_questions["nps"]["page_id"]
    question_id = target_questions["nps"]["question_id"]
    return survey_id, page_id, question_id

def get_responses(survey_id, page_id, question_id):
  answer_array = {}
  for response_id, response in response_data[survey_id].items():    
    for page in response["pages"]:
      if page["id"] == page_id:          
        for question in page["questions"]:
          if question["id"] == question_id:          
            answer_id = question["answers"][0]["choice_id"]
            if answer_id in answer_array:
              answer_array[answer_id] += 1
            else:
              answer_array[answer_id] = 1
  return answer_array

def match_answers(survey_id, page_id, question_id, answer_array):
  for survey in survey_data:
    if survey['id'] == survey_id:
      choices = survey["pages"][0]["questions"][0]["answers"]["choices"]
      for choice in choices:
        answer_array[choice["text"]] = answer_array.pop(choice["id"])
    return answer_array

def calculate_nps(matched_answers):
  for key, value in matched_answers.items():
     
    promoters = (matched_answers["10 (Yes, absolutely)"] + matched_answers["9"])
    passives = (matched_answers["8"] + matched_answers["7"])
    detractors = (matched_answers["6"] + matched_answers["5"] + matched_answers["4"] + matched_answers["3"] + matched_answers["2"] + matched_answers["1 (no way)"])
    total = promoters + passives + detractors
    nps = round((promoters - detractors)/total*100)
    return nps

survey_id, page_id, question_id = get_nps_question(target_surveys)
nps_answers = get_responses(survey_id, page_id, question_id)
matched_answers = match_answers(survey_id, page_id, question_id, nps_answers)
nps = calculate_nps(matched_answers)
