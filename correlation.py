from target_questions import Target
from survey_data import Survey
from response_data import Response
import math
import json
import plotly
from plotly import tools
from plotly.graph_objs import Scatter, Layout

survey_data = Survey.survey_data
target_surveys = Target.target_info
response_data = Response.response_data

def get_ids(question_info):
  survey_id = question_info["survey_id"]
  nps_page_id = question_info["nps"]["page_id"]
  nps_question_id = question_info["nps"]["question_id"]
  components_page_id = question_info["components"]["page_id"]
  components_question_id = question_info["components"]["question_id"]
  return survey_id, nps_page_id, nps_question_id, components_page_id, components_question_id

def get_questions(survey_id, target_survey, ):
  id_info = {}
  id_info["nps"] = {}
  id_info["components"] = {}
  target_questions = target_survey["questions"]
  id_info["survey_id"] = survey_id
  id_info["nps"]["page_id"] = target_questions["nps"]["page_id"]
  id_info["nps"]["question_id"] = target_questions["nps"]["question_id"]
  id_info["components"]["page_id"] = target_questions["components"]["page_id"]
  id_info["components"]["question_id"] = target_questions["components"]["question_id"]
  return id_info 

def get_indexes(survey, question_info):
  survey_id, nps_page_id, nps_question_id, components_page_id, components_question_id = get_ids(question_info)
  nps_page_index = None
  nps_question_index = None
  components_page_index = None
  components_question_index = None
  for page in survey["pages"]:
    if page["id"] == nps_page_id:  
      nps_page_index = survey["pages"].index(page)
      for question in survey["pages"][nps_page_index]["questions"]:
        if question["id"] == nps_question_id:  
          nps_question_index = survey["pages"][nps_page_index]["questions"].index(question)
    if page["id"] == components_page_id:  
      components_page_index = survey["pages"].index(page)
      for question in survey["pages"][components_page_index]["questions"]:
        if question["id"] == components_question_id:  
          components_question_index = survey["pages"][components_page_index]["questions"].index(question)
  return nps_page_index, nps_question_index, components_page_index, components_question_index

def get_index(content_list, content_id): 
  return content_list.index(item)        

def get_responses(question_info):
  event_answers = {}
  survey_id, nps_page_id, nps_question_id, components_page_id, components_question_id = get_ids(question_info)
  for event_id, responses in response_data.items():  
    if survey_id == event_id:
      event_answers[survey_id] = {}
      for response_id, response in responses.items():
        data = {}
        nps_flag = None
        components_flag = None
        for page in response["pages"]:
          if page["id"] == nps_page_id:
            for question in page["questions"]:
              if question["id"] == nps_question_id:
                data["nps_answer"] = question["answers"][0]["choice_id"]
                nps_flag = True
          if page["id"] == components_page_id:
            for question in page["questions"]:
              if question["id"] == components_question_id:
                data["components_answers"] = {}
                for answer in question["answers"]:
                  data["components_answers"][answer["row_id"]] = answer["choice_id"]
                  components_flag = True
        if nps_flag and components_flag:
          event_answers[event_id][response_id] = data
  return event_answers

def get_index(content_list, content_id): 
  return content_list.index(item)        

def get_indexes(survey, question_info):
  survey_id, nps_page_id, nps_question_id, components_page_id, components_question_id = get_ids(question_info)
  nps_page_index = None
  nps_question_index = None
  components_page_index = None
  components_question_index = None
  for page in survey["pages"]:
    if page["id"] == nps_page_id:  
      nps_page_index = survey["pages"].index(page)
      for question in survey["pages"][nps_page_index]["questions"]:
        if question["id"] == nps_question_id:  
          nps_question_index = survey["pages"][nps_page_index]["questions"].index(question)
  for page in survey["pages"]:
    if page["id"] == components_page_id:  
      components_page_index = survey["pages"].index(page)
      for question in survey["pages"][components_page_index]["questions"]:
        if question["id"] == components_question_id:  
          components_question_index = survey["pages"][components_page_index]["questions"].index(question)
  return nps_page_index, nps_question_index, components_page_index, components_question_index

def match_answers(all_answers, question_info):
  survey_id, nps_page_id, nps_question_id, components_page_id, components_question_id = get_ids(question_info)
  for survey in survey_data:
    if survey['id'] == survey_id:
      nps_page_index, nps_question_index, components_page_index, components_question_index = get_indexes(survey, question_info)
      nps_choices = survey["pages"][nps_page_index]["questions"][nps_question_index]["answers"]["choices"]
      components_choices = survey["pages"][components_page_index]["questions"][components_question_index]["answers"]["choices"]
      components_rows = survey["pages"][components_page_index]["questions"][components_question_index]["answers"]["rows"]
      for nps_choice in nps_choices:
        for event, answers in all_answers.items():
          for answer_id, answer in answers.items():
            if answer["nps_answer"] == nps_choice["id"]:
              answer["nps_answer"] = nps_choice["text"]
              if answer["nps_answer"].startswith("10"):
                answer["nps_answer"] = "10"
              elif answer["nps_answer"].startswith("1"):
                answer["nps_answer"] = "1"                
      for components_choice in components_choices:
        for event, answers in all_answers.items():
          for answer_id, answer in answers.items():
            for row, choice in answer["components_answers"].items():
              if choice == components_choice["id"]:
                answer["components_answers"][row] = components_choice["text"]
                if answer["components_answers"][row] == "Excellent":
                  answer["components_answers"][row] = "5"
                elif answer["components_answers"][row] == "Good":
                  answer["components_answers"][row] = "4"
                elif answer["components_answers"][row] == "Fair":
                  answer["components_answers"][row] = "3"
                elif answer["components_answers"][row] == "Poor":
                  answer["components_answers"][row] = "2"
                elif answer["components_answers"][row] == "Very Poor":
                  answer["components_answers"][row] = "1"
      for components_row in components_rows:
        for event, answers in all_answers.items():
          for answer_id, answer in answers.items():
            for row, choice in answer["components_answers"].items():
              if row == components_row["id"]:
                answer["components_answers"][components_row["text"]] = answer["components_answers"].pop(components_row["id"])
  return all_answers

def calculate_correlations(event_type, matched_answers):
  correlations = {}
  flattened_answers = {}
  coordinates = {}
  for survey_id, responses in matched_answers.items():
    for response_id, response in responses.items():
      flattened_answers[response_id] = response
      for component_name, component_value in response["components_answers"].items():
        if component_name not in coordinates:
          coordinates[component_name] = {}
          coordinates[component_name]["coords"] = []
        correlations[component_name] = {}
        correlations[component_name]["n"] = 0
        correlations[component_name]["sum_x"] = 0
        correlations[component_name]["sum_y"] = 0
        correlations[component_name]["sum_xy"] = 0
        correlations[component_name]["sum_x_squared"] = 0
        correlations[component_name]["sum_y_squared"] = 0
        correlations[component_name]["correlation"] = None
  for response_id, response in flattened_answers.items():
    for component_name, component_value in response["components_answers"].items():
      if component_value != "Not Applicable":
        x = int(response["nps_answer"])
        y = int(component_value)
        correlations[component_name]["n"] += 1
        correlations[component_name]["sum_x"] += x
        correlations[component_name]["sum_y"] += y
        correlations[component_name]["sum_xy"] += (x * y)
        correlations[component_name]["sum_x_squared"] += (x * x)
        correlations[component_name]["sum_y_squared"] += (y * y)
        coordinates[component_name]["coords"].append([x, y])
  for component_name, stats in correlations.items():
    stats["correlation"] = (stats["n"] * stats["sum_xy"] - stats["sum_x"] * stats["sum_y"]) / math.sqrt((stats["n"] * stats["sum_x_squared"] - stats["sum_x"] * stats["sum_x"]) * (stats["n"] * stats["sum_y_squared"] - stats["sum_y"] * stats["sum_y"]))
  final_coordinates = {}
  for component_name, component_coords in coordinates.items():
    final_coordinates[component_name] = {}
    for coord in component_coords["coords"]:
      tuple_coord = tuple(coord)
      if tuple_coord in final_coordinates[component_name]:
          final_coordinates[component_name][tuple_coord] += 1
      else:
          final_coordinates[component_name][tuple_coord] = 1
  return correlations, final_coordinates

def create_scatter_charts(event_type, coordinates, correlations):
  counter = 0
  for component_name, data in coordinates.items():   
    correlation = round(correlations[component_name]["correlation"], 2)
    final_data = []
    counter += 1 
    x_axis = []
    y_axis = []
    number_responses = []
    total_responses = sum(data.values())
    for coord, num in data.items():
      x_axis.append(coord[0])
      y_axis.append(coord[1])
      number_responses.append(num)
    magnitude = [str(round((x/total_responses*100), 2)) + "%" for x in number_responses]
    bubble_size = [round(x/total_responses*600) for x in number_responses]
    chart_title = "%s NPS Scores vs %s Scores \n Correlation: %s" % (event_type, component_name, correlation)
    final_data.append(Scatter(
        text = magnitude,
        x = x_axis, 
        y = y_axis,
        mode = 'markers',
        marker = dict(
            size = bubble_size,
        )
        ))
    chart_layout = Layout(
      title = chart_title,
      xaxis = dict(
        # tick0=0,
        dtick = 1,
        ticklen = 6,
        range = [0, 12]
      ),
      yaxis = dict(
        dtick = 1,
        ticklen = 6,
        range = [0, 6]
      )
    )
    plotly.offline.plot({
      "data": final_data,
      "layout": chart_layout
    },
      filename = "charts/component_chart_%s.html" % counter
    )
matched_answers = {}
for event_type, event_data in target_surveys.items():
  all_answers = {}
  matched_answers[event_type] = {}
  for survey_id, data in event_data.items():
    question_info = get_questions(survey_id, data)
    answers = get_responses(question_info)
    all_answers.update(answers)
    matched_answers[event_type].update(match_answers(all_answers, question_info))
  correlations, coordinates = calculate_correlations(event_type, matched_answers[event_type])
  create_scatter_charts(event_type, coordinates, correlations)
  correlations.pop("Group Discussions", None)
  correlations.pop("Short Takes / TAD Talks", None)
  correlations.pop("Think Tanks", None)
  for component_name, scores in correlations.items():
    print (event_type + " " + component_name + ": " + str(round(scores["correlation"], 2)))