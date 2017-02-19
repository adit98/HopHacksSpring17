from flask import Flask
from flask_ask import Ask, statement, question, session
import json
import requests
import time
from collections import deque
import infermedica_api
infermedica_api.configure(app_id='32d6b77a', app_key='fd3b7c019eb63aa649b61c5fed4433c5')
api = infermedica_api.get_api()
request = infermedica_api.Diagnosis(sex='male', age=35) 
numPasses = 0

path = deque()

from numpy import genfromtxt
ami_data = genfromtxt('Secondary_AMI.csv', delimiter=',')
ami_data = ami_data[1:,2:]
y_train =ami_data[:,0]
ami_data = ami_data[:,1:]

from sklearn.ensemble import RandomForestClassifier
secondary_ami_model = RandomForestClassifier()
secondary_ami_model.fit(ami_data, y_train)

from datetime import datetime 
curr_date = datetime.now().strftime('%Y-%m-%d').split("-")
months_dict = {1:"January", 2:"February", 3:"March", 4:"April", 5:"May", 6:"June", 7:"July", 8:"August", 9:"September", 10:"October", 11:"November", 12:"December"}
curr_date = months_dict[int(curr_date[1])] + " " + curr_date[2] + ", " + curr_date[0]
 
import numpy as np
history_illness_db = np.load("history.db.npy")
init = np.array([["Feb 18, 2017",  "Myocardial Infarction"]])
history_illness_db = init

app = Flask(__name__)

ask = Ask(app, "/")

@app.route('/')
def homepage():
	return "Hi, welcome to medic"

@ask.launch
def welcome():
	path.appendleft("home")
	msg = "Hi there, I am Alexa Medic. How are you? Are you feeling sick?"
	msg = "OK. Next"
	return question(msg)

@ask.intent("NeedIntent")
def decisionTree(need):
	if need == "history":
		path.append("history")
		msg = "Would you like your complete history?"
		return question(msg)
	if need == "sick": # nlp
		path.append("diagnosis")
		msg = "Ah, so I see you are sick. Would you like a diagnosis?"
		return question(msg)
	elif need == "insurance": # nlp
		msg = "OK, let me consult your medical insurance provider. Ah, so I see you have Obama care. Unfortunately, the ACA was repealed as of January 5th, 2017. I'm tilted."
		return statement(msg)

@ask.intent('YesIntent')
def yesIntent():
	print path[-1]
	if path[-1] == "history":
		msg = "Here is the medical history I have recorded:"
		for incidence in history_illness_db:
			msg += incidence[0] + ", " + incidence[1] + ". "
		msg += "OK. What now?"
		return question(msg)
	elif path[-1] == "diagnosis":
		msg = "Please list out your symptoms, one by one, and I will try to help."
		return question(msg)
	elif path[-1] == "diagnosis_repeat":
		msg = "OK. What now?"
		return question(msg)
	elif path[-1] == "diagnosis_final":
		history_of_diseases = len(history_illness_db[:,1])
		ami_comorbidities = ["Chest Pain", "Vomiting", "Dizziness", "Shortness of Breath", "Sweating", "Nausea", "Anxiety", " Fast Heart Rate", "Heartburn"]
		numComorbidities = len([filter(lambda x: x in history_of_diseases, sublist) for sublist in ami_comorbidities])
		prob = secondary_ami_model.predict_proba([1]*numComorbidities + [0]*189)[0]
		msg = "According to my model, you have a " + " percent chance of having another myocardial infarction. We recommend you see a doctor. Would you like to be recommended a doctor?"



def getSymptoms(rawData):
	return api.parse(rawData, include_tokens = True)

@ask.intent('SymptomIntent')
def processSymptoms(symptom):
	global history_illness_db, request

	symptoms = getSymptoms(symptom)
	actualSymps = ""

	n = 0
	while(n < len(symptoms.mentions)):
		print symptoms.mentions[n].name.encode('ascii','ignore')
		if symptoms.mentions[n].choice_id.encode('ascii','ignore') == 'present':
			actualSymps += symptoms.mentions[n].name.encode('ascii','ignore') + " "
			history_illness_db = np.vstack((history_illness_db, np.array([curr_date, symptoms.mentions[n].name.encode('ascii','ignore')])))
			request.add_symptom(symptoms.mentions[n].id.encode('ascii','ignore'), symptoms.mentions[n].choice_id.encode('ascii','ignore'))
		n += 1

	np.save("history.db.npy", history_illness_db)
	
	request = api.diagnosis(request)	

	msg = ""
	if (numPasses < 5 and request.question.items[0]['id'] != ""):
		path.append("diagnosis_repeat")
		msg = "Do you have " + request.question.items[0]['name'].encode('ascii','ignore')
	else:
		path.append("diagnosis_final")
		msg = "OK. I noticed that you have a history of recurring problems associated with myocardial infarction within the past weak.\
		Would you like a diagnosis?"
	return question(msg)

#ami_comorbidities= ["Chest Pain", "Vomiting", "Dizziness", "Shortness of Breath", "Sweating", "Nausea", "Anxiety", " Fast Heart Rate", "Heartburn"]
#ami_comorbidities = ["Shortness of breadth", "Dizziness", "Fast Heart Rate"]
#@ask.intent("AMIIntent")


#@ask.intent("RiskIntent")
#def modelTrain(comorbidities):
#	msg = "OK. I noticed that you have a history of recurring problems associated with myocardial infarction. 
#	return question(msg)


@ask.intent('NoIntent')
def quit():
	msg = "I'M TILTED"
	return statement(msg)

if(__name__=='__main__'):
	app.run(debug=True)
