from datetime import datetime as dt
from time import sleep
from configparser import ConfigParser
import os

from selenium import webdriver
import requests


class Client:
    ROOT_URL = 'https://accounts.spotify.com'
    REQUEST_URL = ROOT_URL + '/authorize'
    TOKEN_URL = ROOT_URL + '/api/token'
    REDIRECT_URI = 'https://duckduckgo.com/'

    def __init__(self, user, scope=None, path='client.ini'):
        """
        Gets a access token based on a user.

        Parameters:
        user - The name of the Spotify user
        path - (default 'client.ini') The path to the .ini file with at least
        the client ID and client secret under CLIENT and the path to the
        geckodriver.exe under MISC. Can also have cached refresh tokens under
        USERNAME SCOPE
        scope - (default None) The scope used to get the token, it determines
        what the app is allowed to do/what the user agrees to. Look here for
        them all: https://developer.spotify.com/web-api/using-scopes/
        """
        self.user = user
        self.path = path
        self.scope = scope or ''

        # config stores the data from the .ini file
        self.config = ConfigParser()
        self.config.read(self.path)
        self.client_id, self.client_secret = self.config['CLIENT'].values()
        self.geckodriver_path = self.config['MISC']['geckodriver']

        self.access_token, self.token_birth = self.get_token()

    def get_token(self):
        """
        Will get the access token and a time stamp of when it was made. If a
        refresh token exists for the user/scope combo, then use that to get
        a new one. Otherwise, go through the whole process.
        """
        # Checks to see if there already is a refresh token in the .ini file
        cache_section = self.user + ' ' + self.scope
        if  cache_section in self.config.sections():
            # Takes it if so
            self.refresh_token = self.config[cache_section].values()

            # POSTs to get a new access token
            data = {'grant_type': 'refresh_token', 'refresh_token': self.refresh_token}
            auth = (self.client_id, self.client_secret)
            token = requests.post(self.TOKEN_URL, data=data, auth=auth).json()

            # Return current time as its "birthdate" to determine if expired
            return token['access_token'], dt.now()
        else:
            # Do everything fresh if not in cache (i.e. .ini file)
            return self._request_token()

    def _request_auth_url(self):
        """
        Gets the URL for authenticating the user (URL where they will have
        to log in).
        """
        params = {'client_id': self.client_id, 'response_type': 'code',
                  'redirect_uri': self.REDIRECT_URI, 'scope': self.scope}
        return requests.get(self.REQUEST_URL, params=params).url

    def _get_code(self):
        """
        Gets a string called 'code' that appears in the URL after logging in
        and being redirected to REDIRECT_URI. So this gets that code and closes
        the browser. At the moment, ONLY WORKS WITH FIREFOX. Also, could prob
        do the waiting parts better than while sleep loops, but this works for
        now so I'm gonna keep it.
        """
        auth_url = self._request_auth_url()

        # Open Firefox browser
        browser = webdriver.Firefox(executable_path=self.geckodriver_path)

        # Load authentication URL
        browser.get(auth_url)

        # Wait until login button is pressed
        while browser.current_url.startswith(self.ROOT_URL + '/en/authorize?'):
            sleep(0.1)

        # Automatically fill the username input field
        login_username = browser.find_element_by_id('login-username')
        login_username.send_keys(self.user)

        # Wait until the login is attempted
        while browser.current_url.startswith(self.ROOT_URL):
            sleep(0.1)

        # When it does, strip the code and close the browser
        code = browser.current_url.split('?')[1].split('=')[1]
        browser.close()
        return code

    def _request_token(self, secret=False):
        """
        Using the code from _get_code, gets the access/refresh tokens and
        writes the refresh token to the .ini file.

        Parameters:
        secret - (default False) If True, the refresh token won't be written
                 to the .ini file. 
        """
        # Get the code
        code = self._get_code()

        # POSTs to get the token
        data = {'code': code, 'redirect_uri': self.REDIRECT_URI,
                'grant_type': 'authorization_code'}
        auth = (self.client_id, self.client_secret)
        token = requests.post(self.TOKEN_URL, data=data, auth=auth).json()
        access_token = token['access_token']
        refresh_token = token['refresh_token']

        # Add another section to the .ini file to cache refresh token
        if not secret:
            section_name = self.user + ' ' + self.scope
            self.config.add_section(section_name)
            self.config.set(section_name, 'refresh_token', refresh_token)
            with open(self.path, 'w') as ini_file:
                self.config.write(ini_file)
        self.refresh_token = refresh_token

        # Return the token and its "birthdate"
        return access_token, dt.now()