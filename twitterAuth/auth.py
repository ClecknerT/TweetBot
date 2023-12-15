import os
import tweepy
from requests.auth import AuthBase, HTTPBasicAuth
from requests_oauthlib import OAuth2Session, TokenUpdated
from flask import Flask, request, redirect, session, url_for, render_template

app = Flask(__name__)

# API keys and secrets from your Twitter Developer account
api_key = os.environ.get['api_key']
api_secret = os.environ.get['api_secret']
callback_url = "http://0.0.0.0:5000/callback"  # Replace with your callback URL

@app.route("/")
def index():
    auth = tweepy.OAuth1a(api_key, api_secret, callback_url)
    redirect_url = auth.get_authorization_url()
    return f"Please visit this URL and authorize the app: <a href='{redirect_url}'>{redirect_url}</a>"

@app.route("/callback")
def callback():
    verifier_code = request.args.get("oauth_verifier")
    auth = tweepy.OAuth1a(api_key, api_secret)
    access_token_info = auth.get_access_token(verifier_code)
    access_token = access_token_info[0]
    access_token_secret = access_token_info[1]
    refresh_token = access_token_info[2]
    return f"Access Token: {access_token}<br>Access Token Secret: {access_token_secret}<br>Refresh Token: {refresh_token}"

if __name__ == "__main__":
    app.run(debug=True)
