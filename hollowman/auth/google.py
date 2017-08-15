#encoding: utf-8

from flask_oauthlib.client import OAuth

from hollowman.conf import GOOGLE_OAUTH2_CLIENT_ID, GOOGLE_OAUTH2_CLIENT_SECRET
oauth = OAuth()
google_oauth2 = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          consumer_key=GOOGLE_OAUTH2_CLIENT_ID,
                          consumer_secret=GOOGLE_OAUTH2_CLIENT_SECRET
                )
