#################################
###### Imports ##################
#################################

import requests
import json
import datetime
import sys, clipboard,shortcuts


#################################
###### Assets ###################
#################################

###### Todoist API Token
token='<PLACE TODOIST TOKEN HERE>'

today = datetime.datetime.now()



###### Define headers and paramaters for Todoist Request (documentation available here: https://developer.todoist.com/sync/v8/)
params={'token':token, 'limit':200}

headers={'Authorization': 'Bearer '+token }



#################################
###### Get Data #################
#################################

###### Define function to get summary data for any specified window of time
def get_weekly_data(total_days,params):
	url='https://api.todoist.com/sync/v8/completed/get_all'
	
	###### Build Parameters
	since_date_dt = today - datetime.timedelta(days=total_days)
	since_date = since_date_dt.strftime("%Y-%-m-%dT")+'00:00Z' #2007-4-29T10:13
	params['since']=since_date
	params['offset'] = 0
	
	response=requests.get(url,params=params).json()

	weekly_data = {'items': []
					,'projects': []}

	weekly_data['items'] = response['items']
	weekly_data['projects'] = response['projects'].copy()

	while len(response['items']) == 200:
		params['offset'] += 200
		response=requests.get(url,params=params).json()
		weekly_data['items'] += response['items']
		weekly_data['projects'].update(response['projects'])
	
	return weekly_data



###### Define function to get project information
def get_project_info(project_id,headers,parent):
	url='https://api.todoist.com/rest/v1/projects/' + project_id

	response=requests.get(url,headers=headers).json()

	if parent == 1 and 'parent_id' in response:
		project_id = str(response['parent_id'])
		url='https://api.todoist.com/rest/v1/projects/' + project_id

		response=requests.get(url,headers=headers).json()


	return response


def get_hex_color(color_id):
	colors = {	30: '#b8256f',
				31: '#db4035',
				32: '#ff9933',
				33: '#fad000',
				34: '#afb83b',
				35: '#7ecc49',
				36: '#299438',
				37: '#6accbc',
				38: '#158fad',
				39: '#14aaf5',
				40: '#96c3eb',
				41: '#4073ff',
				42: '#884dff',
				43: '#af38eb',
				44: '#eb96eb',
				45: '#e05194',
				46: '#ff8d85',
				47: '#808080',
				48: '#b8b8b8',
				49: '#ccac93'
				}

	return colors[color_id]			


def get_all_projects(headers):
	url = 'https://api.todoist.com/rest/v1/projects'
	response=requests.get(url,headers=headers).json()

	return response




last_90_days = get_weekly_data(35,params)

date_ranges = {}

for i in range(5):
	date_ranges[i] = today - datetime.timedelta(days=((i+1)*7))


completed_counts = {}
project_parents = {}
project_colors = {}
project_names = {}

all_projects = get_all_projects(headers)
projects_in_report = [key for key in last_90_days['projects']]

for project in all_projects:

	if str(project['id']) in projects_in_report:
		project_data = get_project_info(str(project['id']),headers,1) 

		project_key = project_data['id']
		
		project_parents[project['id']] = project_key
		project_colors[project_key] = get_hex_color(project_data['color'])
		project_names[project_key] = project_data['name']

		completed_counts[project_key] = {}

		for key in date_ranges:
			completed_counts[project_key][key] = 0


for task in last_90_days['items']:
	completed_date = datetime.datetime.strptime(task['completed_date'], "%Y-%m-%dT%H:%M:%SZ")
	
	task_new_project_id = project_parents[task['project_id']]

	for key in date_ranges:
		if key == 0 and completed_date > date_ranges[key]:
			completed_counts[task_new_project_id][key]+= 1
		elif completed_date > date_ranges[key] and completed_date <= date_ranges[key-1]:
			completed_counts[task_new_project_id][key]+= 1	


results = ''


for i in range(4,-1,-1):
	results = results + date_ranges[i].strftime("%Y-%-m-%d")
	if i > 0: 
		results = results +	'\n'

results = results +'~'

for project in completed_counts:
	check_total = 0
	for key in completed_counts[project]:
		check_total+=completed_counts[project][key]

	if check_total > 0:

		project_string = project_names[project] + ' - '
		
		for i in range(4,-1,-1):
			project_string= project_string +str(completed_counts[project][i])

			if i > 0: 
				project_string = project_string +	','

		project_string = project_string + ' - ' + project_colors[project]

		project_string = project_string +	'\n'

		results = results + project_string

# print(results)

clipboard.set(results)

shortcuts.open_shortcuts_app()




