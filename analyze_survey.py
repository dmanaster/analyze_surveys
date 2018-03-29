# what would be valuable is to track results on the areas of the event 
# (i.e. reg, hotel, networking, etc) against previous survey results 
# by brand - possible?

from target_questions import Target
from survey_data import Survey
from response_data import Response

survey_data = Survey.survey_data
target_surveys = Target.target_info
response_data = Response.response_data

def get_questions(survey_id, target_survey, question_types):
  id_info = {}
  target_questions = target_survey["questions"]
  id_info["survey_id"] = survey_id
  for question_type in question_types:
    id_info[question_type] = {}
    id_info[question_type]["page_id"] = target_questions[question_type]["page_id"]
    id_info[question_type]["question_id"] = target_questions[question_type]["question_id"]
  return id_info 

def get_index(content_list, content_id): 
  return content_list.index(item)        

def initialize_answer_array(question_type, question_info):
  survey_id, page_id, question_id = get_ids(question_info)
  answer_array = {}
  for survey in survey_data:
    if survey['id'] == survey_id:
      page_index, question_index = get_indexes(survey, question_info)
      if question_type == "nps":
        choices = survey["pages"][page_index]["questions"][question_index]["answers"]["choices"]
        for choice in choices:
          answer_array[choice["id"]] = 0
      elif question_type == "components":
        rows = survey["pages"][page_index]["questions"][question_index]["answers"]["rows"]
        choices = survey["pages"][page_index]["questions"][question_index]["answers"]["choices"]
        for row in rows:
          answer_array[row["id"]] = {}
          for choice in choices:
            answer_array[row["id"]][choice["id"]] = 0
  return answer_array

def get_ids(question_info):
  survey_id = question_info["survey_id"]
  page_id = question_info[question_type]["page_id"]
  question_id = question_info[question_type]["question_id"]
  return survey_id, page_id, question_id 

def get_nps_responses(question_info):
  survey_id, page_id, question_id = get_ids(question_info)
  answer_array = initialize_answer_array(question_type, question_info)
  for response_id, response in response_data[survey_id].items():    
    for page in response["pages"]:
      if page["id"] == page_id:          
        for question in page["questions"]:
          if question["id"] == question_id:          
            answer_id = question["answers"][0]["choice_id"]
            answer_array[answer_id] += 1
  return answer_array

def get_component_responses(question_info):
  survey_id, page_id, question_id = get_ids(question_info)
  answer_array = initialize_answer_array(question_type, question_info)
  for response_id, response in response_data[survey_id].items():    
    for page in response["pages"]:
      if page["id"] == page_id:          
        for question in page["questions"]:
          if question["id"] == question_id:
            for answer in question["answers"]:
              row_id = answer["row_id"]
              choice_id = answer["choice_id"]
              answer_array[row_id][choice_id] += 1
  return answer_array

def get_indexes(survey, question_info):
  survey_id, page_id, question_id = get_ids(question_info)
  page_index = None
  question_index = None
  for page in survey["pages"]:
    if page["id"] == page_id:  
      page_index = survey["pages"].index(page)
      for question in survey["pages"][page_index]["questions"]:
        if question["id"] == question_id:  
          question_index = survey["pages"][page_index]["questions"].index(question)
  return page_index, question_index

def match_answers(question_type, question_info, answer_array):
  survey_id, page_id, question_id = get_ids(question_info)
  for survey in survey_data:
    if survey['id'] == survey_id:
      page_index, question_index = get_indexes(survey, question_info)
      choices = survey["pages"][page_index]["questions"][question_index]["answers"]["choices"]
      if question_type == "nps":
        for choice in choices:
          answer_array[choice["text"]] = answer_array.pop(choice["id"])
      elif question_type == "components":
        rows = survey["pages"][page_index]["questions"][question_index]["answers"]["rows"]
        for row in rows:
          answer_array[row["text"]] = answer_array.pop(row["id"])
          for choice in choices:
            answer_array[row["text"]][choice["text"]] = answer_array[row["text"]].pop(choice["id"])
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

def calculate_averages(matched_answers):
  averages_dict = {}
  for key, value in matched_answers.items():
    total = 0
    e = value["Excellent"] * 10
    g = value["Good"] * 8
    f = value["Fair"] * 6
    p = value["Poor"] * 4
    vp = value["Very Poor"] * 2
    for description, count in value.items():
      total += count
    weighted_average = (e + g + f + p + vp)/total
    averages_dict[key] = weighted_average
  return averages_dict

question_types = ["nps", "components"]
for event_type, event_data in target_surveys.items():
  for survey_id, data in event_data.items():
    question_info = get_questions(survey_id, data, question_types)
    for question_type in question_types:
      if question_type == "nps":
        answers = get_nps_responses (question_info)
        matched_answers = match_answers(question_type, question_info, answers)
        nps = calculate_nps(matched_answers)
        print(data["title"] + " : " + str(nps))
      elif question_type == "components":
        answers = get_component_responses(question_info)
        matched_answers = match_answers(question_type, question_info, answers)
        averages = calculate_averages(matched_answers)
        for key, average in averages.items():
          print (data["title"] + " " + key + ": " + str(average))