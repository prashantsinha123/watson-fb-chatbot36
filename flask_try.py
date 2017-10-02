from flask import Flask, request, g
import requests
import json
import traceback
from watson_developer_cloud import ConversationV1
from database import db_session


conversation = ConversationV1(
    username= "b97f4e29-766b-46d4-aed8-a0ad9b793991",
    password =  "jIlhixVovYEg",
    version='2017-03-23'
)
# replace with your own workspace_id
workspace_id = '7faf61c3-b769-4834-a695-e817080705d5'

#Token for facebook page
token = "EAACB8TOcWdsBABc1Px8qlQdpDsUvK7Dz3conLYZCW9MX9RIhmnhQ9IjkT3Ez2DxbfNl6EB5izylEWKWcgybEpeTlf0njwFuw8G0AhGZAOZBGwFnZC247HO7cvNFChk8rbnRAbUJodlfueRCiLlWLzZCt0Sf6EHUu90QLAoRrWmcAItkAiTX7W"

app = Flask(__name__)

#flask will automatically remove database sessions at the end of the request or when the application shuts down
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

#initializing the context dictionary before the starting of the conversation
@app.before_request
def initialize():
    global context
    global response
    if not response:
        context = {}
    else :
        context = response['context']

#Initializing global variables
context = {}
response = {}
count = 1

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():

    if request.method == 'POST':
        try:
            data = json.loads(request.data)
            text = data['entry'][0]['messaging'][0]['message']['text']  # Incoming Message Text
            sender = data['entry'][0]['messaging'][0]['sender']['id']  # Sender ID
            global count
            # print "count was " + str(count)
            count += 1
            global context
            print ("data recieved is : ")
            print (json.dumps(data,indent=2))
            print ("context used to obtain response was : ")
            print (json.dumps(context, indent=2))
            global response

            #do these steps only if request is coming from facebook api
            if data['entry'][0]['messaging'][0]['message'].get('is_echo') is None:
                response = conversation.message(workspace_id=workspace_id, message_input={
                    'text': text}, context=context)  # response by watson api
                # print "response is : "
                # print (json.dumps(response, indent=2))
                context = response['context']
                # print "context is :"
                # print context
                #process_response(sender)
                try:
                    reply = ""
                    for text in response['output']['text']:
                        reply = reply + text + "\n"
                    # print "reply is : \n"
                    # print reply
                    payload = {'recipient': {'id': sender}, 'message': {'text': reply}}  # We're going to send this back
                    r = requests.post('https://graph.facebook.com/v2.6/me/messages/?access_token=' + token,
                                      json=payload)  # Lets send it
                except Exception as ex:
                    print ("exception is :")
                    print (ex)


        except Exception as e:
            print ("Error begins")
            print(traceback.format_exc())  # something went wrong
            print ("Error ended")
    elif request.method == 'GET':  # For the initial verification
        if request.args.get(
                'hub.verify_token') ==  "judgement_day":
            return request.args.get('hub.challenge')
        return "Wrong Verify Token"
    return "Hello World!!!"  # Not Really Necessary



@app.route('/')
def hello_world():
    return "Hello World!!!!"


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)


