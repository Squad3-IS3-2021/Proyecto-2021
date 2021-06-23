from flask import Flask, request, jsonify, redirect, Response
import pycronofy
import os
from datetime import datetime
import pickle
import pytz

CLIENT_ID = '_EnkRaQwvl4aI9_5892h_AIUtI2TpvJ_'
CLIENT_SECRET = 'tZDDBnlupQbP_seiAj2ccuTCIxvEhvKFLMgC1NDnLxNYF94hNdMsg-_an1VqsFSXTE1TlSnktDzOr7zfbD3jXA'
CRED_PATH = '../credentials/credential.txt'

app = Flask(__name__)
app.config["DEBUG"] = True


cronofy = pycronofy.Client(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)


def isLoggedIn():
    try:
        reply = cronofy.account()
        return True
    except:
        return Response('Not Logged In', status=401)


@app.route('/', methods=['GET'])
def home():
    return jsonify(
        message='hello-world'
    )
@app.route('/getAccountDetails', methods=['GET'])
def getAccDetails():
    if isLoggedIn():
        return jsonify(cronofy.account())
    return Response('Not Logged In', status=401)

@app.route('/getCalendars', methods=['GET'])
def getCalendars():
    if isLoggedIn():
        return jsonify(cronofy.list_calendars())
    return Response('Not Logged In', status=401)

@app.route('/getGoogleCalId', methods=['GET'])
def getGoogleCalId():
    if isLoggedIn():
        return jsonify(calendar_id = ((cronofy.list_calendars())[0])['calendar_id'])
    return Response('Not Logged In', status=401)

@app.route('/getAuthCode', methods=['GET'])
def testURL():
    # Initial authorization, we send an auth link that the frontend must show to the user. User clicks and API gets a petition to authCallback, creating credentials.txt
    print(cronofy)
    url = cronofy.user_auth_link('http://localhost:8000/authCallback')

    return jsonify(
        authURL=url
    )

@app.route('/authCallback', methods=['POST', 'GET'])
def authCallback():
    global cronofy

    #Receiving authorization code
    code = request.args.get('code')
    auth = cronofy.get_authorization_from_code(code)
    print('Type of token_expiration:') 
    print( auth['token_expiration'])
    
    #Save auth contents into file
    with open(CRED_PATH, 'wb') as f:
        pickle.dump(auth, f)
        f.close()

    #Creating a client including all auth code
    cronofy = pycronofy.Client(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        access_token=auth['access_token'],
        refresh_token=auth['refresh_token'],
        token_expiration=auth['token_expiration']
    )
    return Response('Auth OK', status=200)
    
@app.route('/getTasks', methods=['POST'])
def getTasks():
    isLoggedIn()
    #FALTA ARREGLAR!!
    from_date = datetime.strptime(request.args.get('from_date'), '%Y-%m-%dT%H:%M:%SZ')
    to_date = datetime.strptime(request.args.get('to_date'), '%Y-%m-%dT%H:%M:%SZ')
    calendar_id = ((cronofy.list_calendars())[0])['calendar_id']
    timezone_id = 'US/Eastern'

    allEvents = cronofy.read_events(
        calendar_ids=(calendar_id,),
        from_date=from_date,
        to_date=to_date,
        tzid=timezone_id
    ).all()

    return jsonify(
        allEvents
    )

@app.route('/setup', methods=['GET'])
def checkCredentials():
    global cronofy
    #if there is no credentials.txt
    if os.path.isfile(CRED_PATH) == False:
        #Create Credentials
        testURL()

    #if there is one, gather its info.
    with open(CRED_PATH, 'rb') as f:
        auth = pickle.load(f)

    print( type(auth['token_expiration']))
    f.close()
    #Change auth expiration token from string to a datetime
    eastern = pytz.timezone('US/Eastern')
    
    auth['token_expiration'] = datetime.strptime(auth['token_expiration']+'UTC', '%Y-%m-%dT%H:%M:%SZ%Z')
    auth['token_expiration'] = eastern.localize(auth['token_expiration'])
    #Check if creds file is format-valid

    #Create the cronofy client using the info we gathered
    cronofy = pycronofy.Client(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        access_token=auth['access_token'],
        refresh_token=auth['refresh_token'],
        token_expiration=auth['token_expiration']
    )

    #Check if creds are time-valid, if not, renew them

    if cronofy.is_authorization_expired():
        #Need to refresh credentials
        auth = cronofy.refresh_authorization()
        #Recreate client using new credentials
        cronofy = pycronofy.Client(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            access_token=auth['access_token'],
            refresh_token=auth['refresh_token'],
            token_expiration=auth['token_expiration']
        )
    return Response('Loaded credentials successfully', status=200)

