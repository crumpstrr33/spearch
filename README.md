# Spearch: Cause Portmanteaus Are In
Pretty much a way to better search Spotify playlists with arbitrary logic.

## Requirements
- Python packages: [Requests](http://docs.python-requests.org/en/master/), [Selenium](https://pypi.python.org/pypi/selenium)
- [Geckodriver](https://github.com/mozilla/geckodriver/releases) for Selenium

## How It Did
- Sign up on the Spotify API and get yourself a client ID and client secret. Don't worry about the client URI, it doesn't matter.
- Create an ini file called *client.ini* and add the following:
```
[CLIENT]
client_id = <client_id>
client_secret = <client_secret>

[MISC]
geckodriver = <absolute_or_relative_path_to_geckodriver.exe>
```
- Using IPython, Jupyter Notebook or the like, create a `Client` object with `client = Client(<username>, <scope>)`. The scope includes the permissions for the login. For now, use:
```
user-modify-playback-state playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public
```
This will get an access and refresh token. The refresh token will be saved for the username and scope in the .ini file.
- Create a `User` object with `user = User(client.access_token, client.token_birth)` and you're good to go.
- Read the docstrings for the functions. Pretty much, filter a playlist, make a queue and then, optionally, make a playlist from it.
