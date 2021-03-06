# Spearch
A way to search your Spotify playlists with more control. Choose the songs you want which are added to a 'Queue Maker'. When satisfied, these songs can be added to a new playlist or a new queue. This code offers the following functionality:
1) Choose songs from any one of your playlists by hand
2) Filter your playlists by song names, artist names, and more
3) Create a queue based on your choices above or even a playlist if you so choose
4) Switch between devices connected to your Spotify account

## Requirements
- Python packages: [Requests](https://pypi.org/project/requests/), [Selenium](https://pypi.python.org/pypi/selenium), [PyQt5](https://pypi.python.org/pypi/PyQt5)
- Firefox cause the login page is opened on Firefox and I'm too lazy to add other browser support
- [Geckodriver](https://github.com/mozilla/geckodriver/releases) so Selenium can work with Firefox

## How To Set This Up
- Sign up on the Spotify API and get yourself a client ID and client secret. Don't worry about the client URI, it doesn't matter.
- Create an ini file called *client.ini* in the root folder and add the following:
```
[CLIENT]
client_id = <client_id>
client_secret = <client_secret>
```
- cd to `spearch/gui` and run `python main.py` and you're good to go.
