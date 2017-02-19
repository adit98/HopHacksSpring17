from flask import Flask
from flask_ask import Ask, statement, question, session
import json
import requests
import time
from collections import deque
path = deque()

from datetime import datetime
curr_date = datetime.now().strftime('%Y-%m-%d').split("-")
months_dict = {1:"January", 2:"February", 3:"March", 4:"April", 5:"May", 6:"June", 7:"July", 8:"August", 9:"September", 10:"October", 11:"November", 12:"December"}
curr_date = months_dict[int(curr_date[1])] + " " + curr_date[2] + ", " + curr_date[0]
 
import numpy as np
history_illness_db = np.load("history.db.npy")

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
		msg = "OK. Next"
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
		return question(msg)
	elif path[-1] == "diagnosis":
		print "yes"
		msg = "Please list out your symptoms, one by one, and I will try to help."
		msg = "OK. Next"
		return question(msg)

@ask.intent('SymptomIntent')
def processSymptoms(symptom):
	global history_illness_db 
	print symptom
	msg = "So. You " + symptom[1:] + ". That is unfortunate. What else do you need?"
	history_illness_db = np.vstack((history_illness_db, np.array([curr_date, symptom])))
	np.save("history.db.npy", history_illness_db)
	return question(msg)

#ami_comorbidities= ["Chest Pain", "Vomiting", "Dizziness", "Shortness of Breath", "Sweating", "Nausea", "Anxiety", " Fast Heart Rate", "Heartburn"]
ami_comorbidities = ["Shortness of breadth", "Dizziness", "Fast Heart Rate"]
@ask.intent("AMIIntent")
def diagnoseSecondaryAMI(ami):
	ami_str = ". ".join(ami_comorbidities) + "?"
	msg = "I noticed that you are have recurring " + ami + " according to your history. In addition you also have had an acute myocardial infarction in the past. In the past week, have you also had any of these comorbidities. Shortness of breadth. Dizziness. Fast Heart Rate?" + 
	return question(msg)

@ask.intent("AllIntent")
def modelTrain(comorbidities):
	ami_str = ". ".join(ami_comorbidities)
	msg = "OK. You said" + ami_str + ". According to my model, you have a: "
	

	return question(msg)


@ask.intent('NoIntent')
def quit():
	msg = "I'M TILTED"
	return statement(msg)

if(__name__=='__main__'):
	app.run(debug=True)
