# what would be valuable is to track results on the areas of the event 
# (i.e. reg, hotel, networking, etc) against previous survey results 
# by brand - possible?

from target_questions import Target
from survey_data import Survey
from response_data import Response
from datetime import datetime
import plotly
from plotly import tools
from plotly.graph_objs import Scatter, Layout, Bar

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
    e = value["Excellent"] * 5
    g = value["Good"] * 4
    f = value["Fair"] * 3
    p = value["Poor"] * 2
    vp = value["Very Poor"] * 1
    for description, count in value.items():
      total += count
    weighted_average = round(((e + g + f + p + vp)/total), 2)
    averages_dict[key] = weighted_average
  return averages_dict

def prepare_chart_data(chart_data):
  x_axis = []
  y_axis = []
  for k, v in chart_data.items():
    x_axis.append(k)
    y_axis.append(v)
  return x_axis, y_axis

def create_nps_chart(nps_chart_data):
  final_data = []
  for event_type, nps_data in nps_chart_data.items():    
    x_axis, y_axis = prepare_chart_data(nps_data)
    if event_type == "SourceCon":
      event_marker = dict(
        size = 10,
        color = 'rgb(103, 174, 68)'
        )
      event_textfont = dict(
        color = 'rgb(103, 174, 68)'
        )
    elif event_type == "ERE Conference":
      event_marker = dict(
        size = 10,
        color = 'rgb(22, 98, 133)'
        )
      event_textfont = dict(
        color = 'rgb(22, 98, 133)'
        )
    chart_title = "Event NPS Scores"
    final_data.append(Scatter(
        x = x_axis, 
        y = y_axis,
        mode='lines+text',
        textposition='top left',
        name = event_type,
        marker = event_marker,
        textfont = event_textfont,
        text = y_axis
        ))
  chart_layout = Layout(
    margin = dict(
      r = 150,
      b = 200,
      ),
    title = chart_title
  )
  plotly.offline.plot({
    "data": final_data,
    "layout": chart_layout
  },
    filename = "charts/nps_chart.html"
  )

def get_component_averages(event_type, data):
  component_averages = {}
  for event_name, averages in data.items():
    if (event_type == ("SourceCon") and event_name.startswith("Source")):
      for component_name, average in averages.items():
        if component_name not in component_averages.keys():
          component_averages[component_name] = []
        component_averages[component_name].append(average)
    elif (event_type == ("ERE Conference") and event_name.startswith("ERE")):
      for component_name, average in averages.items():
        if component_name not in component_averages.keys():
          component_averages[component_name] = []
        component_averages[component_name].append(average)
  for component_name, scores in component_averages.items():
    component_averages[component_name] = round(sum(component_averages[component_name]) / len(component_averages[component_name]), 2)
  return component_averages
    
def create_component_charts(component_chart_data):
  for event_type, event in component_chart_data.items(): 
    final_data = []
    component_averages = get_component_averages(event_type, event)
    event_filename = "charts/" + event_type.lower().replace(" ", "_")+ "_component_chart.html"
    for event_name, averages in event.items():   
      bar_x_axis, bar_y_axis = prepare_chart_data(averages)
      scatter_x_axis, scatter_y_axis = prepare_chart_data(component_averages)
      chart_title = event_type + " Component Scores"
      final_data.append(Bar(
        x = bar_x_axis, 
        y = bar_y_axis,
        textposition='top left',
        name = event_name,
        text = event_name
        )
      )
    chart_layout = Layout(
      margin = dict(
        r = 150,
        b = 200,
        ),
      title = chart_title
      )
    final_data.append(Scatter(
      x = scatter_x_axis, 
      y = scatter_y_axis,
      mode = 'markers',
      name = "Average Score",
      text = "Average Score",
      marker = dict(
        symbol = 'line-ns-open',
        color = 'rgb(0, 0, 0)',
        size = 1,
        line = dict(
          width = 75
          )
        )
      )
    )
    plotly.offline.plot({
      "data": final_data,
      "layout": chart_layout
    },
      filename = event_filename
    )

question_types = ["nps", "components"]
nps_chart_data = {}
component_chart_data = {}
for event_type, event_data in target_surveys.items():
  nps_chart_data[event_type] = {}
  component_chart_data[event_type] = {}
  for survey_id, data in event_data.items():
    question_info = get_questions(survey_id, data, question_types)
    for question_type in question_types:
      if question_type == "nps":
        answers = get_nps_responses (question_info)
        matched_answers = match_answers(question_type, question_info, answers)
        nps = calculate_nps(matched_answers)
        event_name = data["season"] + " " + data["date_created"][:4]
        nps_chart_data[event_type][event_name] = nps
      elif question_type == "components":
        answers = get_component_responses(question_info)
        matched_answers = match_answers(question_type, question_info, answers)
        averages = calculate_averages(matched_answers)
        component_chart_data[event_type][data["title"]] = averages
        # for component, average in averages.items():
create_nps_chart(nps_chart_data)
create_component_charts(component_chart_data)