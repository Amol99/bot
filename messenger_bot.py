from flask import Flask, request
import json
import requests
from Credentials import PAGE_ACCESS_TOKEN,VERIFY_TOKEN
import os
from chatterbotapi import *
import string
import random
#from textblob import TextBlob
from Functions import *
import nltk
from nltk.corpus import stopwords
from nltk.tag import pos_tag
nltk.data.path.append('/nltk_data')
print nltk.data.path
stopset=set(stopwords.words('english') + list(string.punctuation))


app = Flask(__name__)



##############################
#PandoraBot Setup for random responses

factory = ChatterBotFactory()
bot1 = factory.create(ChatterBotType.PANDORABOTS, '84c625bcfe37b4ea')
bot1session = bot1.create_session()
##############################

##############################
#Global initialization
state=0
# Sentences we'll respond with if the user greeted us
GREETING_KEYWORDS = ["hello", 'yo', "hi", "greetings", "sup", "what's up", "hey"]
GREETING_RESPONSES = ['Hi','Hello','Hey','Hi!','Hello!','Hey!']
##############################

###############################
#Check for  Name (If state is 1 then we have to find out the name)
def check_for_Name(sentence):
    x = nltk.word_tokenize(sentence.lower())
    print x
    cleanup=[]
    for i in x:
        if i  not in stopset:
            cleanup.append(i)
    tagged_sent = pos_tag(cleanup)
    print  tagged_sent
    Nouns = [word for word, pos in tagged_sent if pos == 'NN']
    print Nouns
    y = None
    global state
    if len(Nouns)==0:
        y = sentence
    if  len(Nouns)!=0:
        y= Nouns[len(Nouns)-1]
	msg = y.title() + ' what are looking for ?'
	state = 2
	return  msg

###############################
#print check_for_Name('Amol.')

###############################
#Check_For_Greeting (check if State is zero or not if yes then change it to 1)

def check_for_greeting(sentence):
    """If any of the words in the user's input was a greeting, return a greeting response"""
    output=None
    global state
    z = nltk.word_tokenize(sentence)
    print z
    for word in z:
        print word.lower()
        if word.lower() in GREETING_KEYWORDS:
            print 1
            msg = random.choice(GREETING_RESPONSES)
            output = msg + ' I am Phenom Bot, your job search assistant. Welcome, May I know your name please?'
            state = 1
    return output
###############################

#print  check_for_greeting('hey')

#############################
#main processing of response

def process(message):
    global state
    y = check_for_greeting(message)
    if y!=None:
        return y
    elif state == 1:
        y = check_for_Name(message)
    return y
###############################

print  process('Hey, I am  Amol, I  live  in Aurangabad')

@app.route('/', methods=['GET'])
def handle_verification():
    print 'got get request'
    if request.args.get('hub.verify_token', 200) == VERIFY_TOKEN:
        return request.args.get('hub.challenge'), 200
    else:
        return 'Error, wrong validation token'	


@app.route('/', methods=['POST'])
def handle_messages():
    global state
    print 'got post request'
    payload = request.get_data()
    for sender, message in messaging_events(payload):
        msg = process(message)
        print state
        print msg
        if  msg !=None:
        	send_message(PAGE_ACCESS_TOKEN, sender, msg)
        	return 'ok'
        else:	
        	msg = bot1session.think(message)
        	if len(msg) > 320:
        		for j in range(0, (len(msg) / 320), 1):
        			if (j + 1) * 320 <= levn(msg):
        				send_message(PAGE_ACCESS_TOKEN, sender, msg[j * 320:(j + 1) * 320])
        			else:
        				send_message(PAGE_ACCESS_TOKEN, sender, msg[j * 320:])
        	else:
        		send_message(PAGE_ACCESS_TOKEN, sender, msg+':)')
    return 'ok'



#####################

def messaging_events(payload):
    data = json.loads(payload)
    messaging_events = data["entry"][0]["messaging"]
    for event in messaging_events:
        if "message" in event and "text" in event["message"]:
            yield event["sender"]["id"], event["message"]["text"].encode('utf-8')
        else:
            yield event["sender"]["id"], "I can't echo this"


def send_message(token, recipient, text):
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                      params={"access_token": token},
                      data=json.dumps({
                          "recipient": {"id": recipient},
                          "message": {"text": text}
                      }),
                      headers={'Content-type': 'application/json'})
    if r.status_code != requests.codes.ok:
        print r.text

########################        


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


	



