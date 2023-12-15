import main
import json
import os

twitter = main.make_token()
client_id = os.environ.get("client_id")
client_secret = os.environ.get("client_secret")
token_url = "https://api.twitter.com/2/oauth2/token"
refresh_token = ''

refreshed_token = twitter.refresh_token(
    client_id=client_id,
    client_secret=client_secret,
    token_url=token_url,
    refresh_token=refresh_token,
)
st_refreshed_token = '"{}"'.format(refreshed_token)
j_refreshed_token = json.loads(st_refreshed_token)
refresh_token=j_refreshed_token
