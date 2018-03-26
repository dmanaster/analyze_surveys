# what would be valuable is to track results on the areas of the event 
# (i.e. reg, hotel, networking, etc) against previous survey results 
# by brand - possible?

from target_questions import Target
from survey_data import Survey
from response_data import Response

survey_data = Survey.survey_data
target_surveys = Target.target_info
response_data = Response.response_data

def get_question(target_survey, question_type):
  target_questions = target_survey["questions"]
  page_id = target_questions[question_type]["page_id"]
  question_id = target_questions[question_type]["question_id"]
  return page_id, question_id

def get_index(content_list, content_id): 
  return content_list.index(item)        

def initialize_answer_array(survey_id):
  answer_array = {}
  for survey in survey_data:
    if survey['id'] == survey_id:
      page_index, question_index = get_indexes(survey, survey_id, page_id, question_id)
      choices = survey["pages"][page_index]["questions"][question_index]["answers"]["choices"]
      for choice in choices:
        answer_array[choice["id"]] = 0
  return answer_array

def get_responses(survey_id, page_id, question_id):
  answer_array = initialize_answer_array(survey_id)
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

def get_indexes(survey, survey_id, page_id, question_id):
  page_index = None
  question_index = None
  for page in survey["pages"]:
    if page["id"] == page_id:  
      page_index = survey["pages"].index(page)
      for question in survey["pages"][page_index]["questions"]:
        if question["id"] == question_id:  
          question_index = survey["pages"][page_index]["questions"].index(question)
  return page_index, question_index

def match_answers(survey_id, page_id, question_id, answer_array):
  for survey in survey_data:
    if survey['id'] == survey_id:
      page_index, question_index = get_indexes(survey, survey_id, page_id, question_id)
      choices = survey["pages"][page_index]["questions"][question_index]["answers"]["choices"]
      for choice in choices:
        answer_array[choice["text"]] = answer_array.pop(choice["id"])
  return answer_array

def calculate_nps(matched_answers):
  ten_key = None
  one_key = None
  for key, value in matched_answers.items():
    if key.startswith("10 "):
      ten_key = key
    if key.startswith("1 ") or key.startswith("1<"):
      one_key = key
  promoters = (matched_answers[ten_key] + matched_answers["9"])
  passives = (matched_answers["8"] + matched_answers["7"])
  detractors = (matched_answers["6"] + matched_answers["5"] + matched_answers["4"] + matched_answers["3"] + matched_answers["2"] + matched_answers[one_key])
  total = promoters + passives + detractors
  nps = round((promoters - detractors)/total*100)
  return nps

for event_type, event_data in target_surveys.items():
  for survey_id, data in event_data.items():
    question_type = "nps"
    page_id, question_id = get_question(data, question_type)
    nps_answers = get_responses(survey_id, page_id, question_id)
    matched_answers = match_answers(survey_id, page_id, question_id, nps_answers)
    nps = calculate_nps(matched_answers)
    print(data["title"] + " : " + str(nps))