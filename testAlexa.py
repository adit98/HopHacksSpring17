from flask import Flask
from flask_ask import Ask, statement, question, session
import json
import requests
import time

app = Flask(__name__)

ask = Ask(app, "/")

@app.route('/')
def homepage():
	return "Hi, welcome to medic"

@ask.launch
def welcome():
	msg = "Hi there, sorry to hear you aren't feeling well. What do you need?"
	return question(msg)

@ask.intent("NeedIntent")
def DecisionTree(need):
	if need == "sick":
		msg = "Ah, so I see you are sick. Please list out your symptoms, one by one."
		return question(msg)
	elif need == "insurance":
		msg = "OK, let me consult your medical insurance provider. Ah, so I see you have Obama care. Unfortunately, the ACA was repealed as of January 5th, 2017. I'm tilted."
		return statement(msg)

@ask.intent('YesIntent')
def askForSymptoms():
	msg = "Please list out your symptoms, one by one."
	return question(msg)

@ask.intent('ProcessIntent')
def processSymptoms(symptom):
	print symptom
	msg = "Your symptoms are ... Nausea ... Dizziness ... Chest Pain"
	return statement(msg)


@ask.intent('NoIntent')
def quit():
	msg = "I'M TILTED"
	return statement(msg)


if(__name__=='__main__'):
	app.run(debug=True)
