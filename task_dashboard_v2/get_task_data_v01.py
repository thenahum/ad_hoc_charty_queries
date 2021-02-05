################################################
###### Get Time Dash Data v1.0 #################
###### Created by: Nahum Garcia ################
################################################


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

	weekly_data = {'items': []}

	weekly_data['items'] = response['items']

	while len(response['items']) == 200:
		params['offset'] += 200
		response=requests.get(url,params=params).json()
		weekly_data['items'] += response['items']
	
	return weekly_data


last_90_days = get_weekly_data(91,params)



date_ranges = {}

for i in range(13):
	date_ranges[i] = today - datetime.timedelta(days=((i+1)*7))


completed_counts= {}

for key in date_ranges:
	completed_counts[key] = 0


for task in last_90_days['items']:
	completed_date = datetime.datetime.strptime(task['completed_date'], "%Y-%m-%dT%H:%M:%SZ")

	for key in date_ranges:
		if key == 0 and completed_date > date_ranges[key]:
			completed_counts[key]+= 1
		elif completed_date > date_ranges[key] and completed_date <= date_ranges[key-1]:
			completed_counts[key]+= 1	

results = ''

for i in range(13):
	results = results + str(i) 
	if i < 12: 
		results = results +	','

results = results +'\n'

for i in range(12,-1,-1):
	results= results +str(completed_counts[i])
	if i > 0: 
		results = results +	','

results = results +'\n'

for i in range(12,-1,-1):
	results = results + date_ranges[i].strftime("%Y-%-m-%d")
	if i > 0: 
		results = results +	','


clipboard.set(results)

shortcuts.open_shortcuts_app()


