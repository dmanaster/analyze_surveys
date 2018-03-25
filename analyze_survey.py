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
    nps_question = target_questions["nps"]
    return survey_id, nps_question

def get_responses(survey_id, nps_question):
  answer_array = {}
  for response_id, response in response_data[survey_id].items():    
    for page in response["pages"]:
      for question in page["questions"]:
        if question["id"] == nps_question:          
          answer = question["answers"][0]["choice_id"]
          if answer in answer_array:
            answer_array[answer] += 1
          else:
            answer_array[answer] = 1
  return answer_array

      # for question_id, question in page["questions"].items():
      #   if question["id"] == nps_question:
      #     print(question)



survey_id, question = get_nps_question(target_surveys)
nps_answers = get_responses(survey_id, question)
print (nps_answers)