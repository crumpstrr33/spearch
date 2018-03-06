# Spearch: Cause Portmanteaus Are In
Pretty much a way to better search Spotify playlists. Gonna add more stuff as I figure out what to add and how to add it.

## Requirements
- Python packages: [Requests](http://docs.python-requests.org/en/master/), [Selenium](https://pypi.python.org/pypi/selenium), [PyQt5](https://pypi.python.org/pypi/PyQt5)
- [Geckodriver](https://github.com/mozilla/geckodriver/releases) for Selenium
- Firefox cause the login page is opened on Firefox and I'm too lazy to add other browser support

## How To Set This Bad Boy Up
- Sign up on the Spotify API and get yourself a client ID and client secret. Don't worry about the client URI, it doesn't matter.
- Create an ini file called *client.ini* in the root folder and add the following:
```
[CLIENT]
client_id = <client_id>
client_secret = <client_secret>
```
- cd to `spearch/gui` and run `python main.py`. There's limited functionality for this at the moment since I suck with Qt. There's more functions on the backend (in `user.py`) that I will slowly get to adding.
