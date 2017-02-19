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
	msg = "Hi there, sorry to hear you aren't feeling well. Do you need me to assist you?"
	return question(msg)

@ask.intent('YesIntent')
def askForSymptoms():
	msg = "Please list out your symptoms, one by one."
	return question(msg)

@ask.intent('ProcessIntent')
def processSymptoms(bigStr):
	#symptoms = bigStr.split()
	msg = "Your symptoms are " + bigStr
	return statement(msg)


@ask.intent('NoIntent')
def quit():
	msg = "jesus bout to fuck you up"
	return statement(message)


if(__name__=='__main__'):
	app.run(debug=True)
