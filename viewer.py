import requests


class Viewer:
    """
    Gets info that doesn't require login.

    Parameters:
    user - The Spotify user
    """
    API_URL = 'https://api.spotify.com'

    def __init__(self, user):
        self.user = user
        self.token = self._get_token()
        self.playlist_names, self.playlist_ids = self._get_playlists()

    def _get_playlists(self):
        """
        Gets the name and ID info for each playlist that the user has.
        """
        # Get data
        url = self.API_URL + '/v1/users/{}/playlists'.format(self.user)
        headers = {'Authorization': 'Bearer ' + self.token}

        # Get the entire JSON and return a list of the names and the IDs
        playlists = requests.get(url, headers=headers).json()
        return [x['name'] for x in playlists['items']], \
               [x['id'] for x in playlists['items']]

    def get_playlist_songs(self, playlist):
        """
        Returns a list of the songs and a list of the artists of each song
        in a playlist given for the user. The list of artists has a list for
        each element since each song can have more than one artist.

        Parameters:
        playlist - The playlist of the user to get the song data for
        """
        # Make sure the the playlist name
        if playlist not in self.playlist_names:
            raise Exception('Playlist {} not found for user {}'.format(
                playlist, self.user))

        # Get playlist ID for given playlist name
        playlist_id = self.playlist_ids[self.playlist_names.index(playlist)]

        # Get data
        url = self.API_URL + '/v1/users/{}/playlists/{}'.format(self.user, playlist_id)
        headers = {'Authorization': 'Bearer ' + self.token}

        # JSON with all the data of the songs
        song_data = requests.get(url, headers=headers).json()['tracks']['items']
        songs, artists = [], []
        # Create lists of each song and the artist(s) for each song
        for song in song_data:
            songs.append(song['track']['name'])
            artists.append([artist['name'] for artist in song['track']['artists']])

        return songs, artists

