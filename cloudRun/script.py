import requests
import base64
import hashlib
import os
import json
import re
import firebase_admin
from firebase_admin import db
from firebase_admin import credentials
from requests.auth import AuthBase, HTTPBasicAuth
from requests_oauthlib import OAuth2Session, TokenUpdated
import google.cloud.logging
import logging

from flask import Flask, request, redirect, session

app = Flask(__name__)
# app.secret_key = os.urandom(50)
logging.basicConfig(level=logging.INFO)
    
# Create a code verifier
code_verifier = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8")
code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)

# Create a code challenge
code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
code_challenge = code_challenge.replace("=", "")

@app.route('/tweet', methods=['POST'])
def tweet():
    try:
        client = google.cloud.logging.Client()
        client.setup_logging()
        cred = credentials.Certificate('/app/serviceAccountCred.json')
        firebase_admin.initialize_app(
            cred, 
            options={
                'databaseURL' : "<your-firestore-url>"
            }
        )
        dbRef = db.reference('twit')
        refresh_token = dbRef.child("refresh_token").get()
        access_token = dbRef.child("access_token").get()

        client_id =  os.environ.get['client_id']
        client_secret = os.environ.get['client_secret']
        access_token= os.environ.get['access_token']
        token_url = "https://api.twitter.com/2/oauth2/token"
        scopes = ["tweet.read", "users.read", "tweet.write", "offline.access"]
        redirect_uri = "https://twit-qy4nptoeha-uc.a.run.app:8080/callback"
        twitter = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scopes)
        refreshed_token = twitter.refresh_token(
            client_id=client_id,
            client_secret=client_secret,
            token_url=token_url,
            refresh_token=refresh_token,
        )
        st_refreshed_token = '"{}"'.format(refreshed_token)
        j_refreshed_token = json.loads(st_refreshed_token)
        refresh_token = j_refreshed_token['refresh_token']
        access_token = j_refreshed_token['access_token']
        dbRef.update({"refresh_token": refresh_token,"access_token": access_token})
        data = request.get_json()
        message = data.get('message')
        return 'Get Media Success:' + message
    except Exception as e:
        return 'Get Media Error: ' + str(e)

@app.route('/auth', methods=['POST'])
def auth():
    client = google.cloud.logging.Client()
    client.setup_logging()
    cred = credentials.Certificate('/app/serviceAccountCred.json')
    firebase_admin.initialize_app(
        cred, 
        options={
            'databaseURL' : "<your-firestore-url>"
        }
    )
    dbRef = db.reference('twit')
    access_token = dbRef.child("access_token").get()
    client_id =  os.environ.get['client_id']
    auth_url = "https://twitter.com/i/oauth2/authorize"
    scopes = ["tweet.read", "users.read", "tweet.write", "offline.access"]
    redirect_uri = "https://twit-qy4nptoeha-uc.a.run.app:8080/callback"
    twitter = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scopes)
    authorization_url, state = twitter.authorization_url(
        auth_url, code_challenge=code_challenge, code_challenge_method="S256"
    )
    session["oauth_state"] = state
    return redirect(authorization_url)


@app.route('/callback', methods=['GET'])
def callback():
    client = google.cloud.logging.Client()
    client.setup_logging()
    cred = credentials.Certificate('/app/carrington-9-0d7370a4c5a9.json')
    firebase_admin.initialize_app(
        cred, 
        options={
            'databaseURL' : 'https://carrington-9-default-rtdb.firebaseio.com/'
        }
    )
    dbRef = db.reference('twit')
    refresh_token = dbRef.child("refresh_token").get()
    access_token = dbRef.child("access_token").get()
    client_id =  os.environ.get['client_id']
    client_secret = os.environ.get['client_secret']
    token_url = "https://api.twitter.com/2/oauth2/token"
    auth_url = "https://twitter.com/i/oauth2/authorize"
    scopes = ["tweet.read", "users.read", "tweet.write", "offline.access"]
    redirect_uri = "https://twit-qy4nptoeha-uc.a.run.app:8080/callback"
    twitter = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scopes)
    code = request.args.get("code")
    token = twitter.fetch_token(
        token_url=token_url,
        client_secret=client_secret,
        code_verifier=code_verifier,
        code=code,
    )
    st_token = '"{}"'.format(token)
    j_token = json.loads(st_token)
    logging.debug('st_token: ', st_token)
    logging.debug('j_token: ', j_token)
    if j_token:
        refresh_token = j_token['refresh_token']
        access_token = j_token['access_token']
        dbRef.update({"refresh_token": refresh_token,"access_token": access_token})
        return 'Token updated successfully.'+ refresh_token
    else:
        logging.error('9999999 No token provided.')
        return 'No token provided.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
