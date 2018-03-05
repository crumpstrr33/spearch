from datetime import datetime as dt
from itertools import compress
from math import ceil
from json import dumps

import requests


"""
Binary operators as functions for the song filtering
"""
def _equiv(x, y):
    return x == y
def _in(x, y):
    return x in y
def _and_iter(l1, l2):
    if len(l1) != len(l2):  
        raise Exception('Lengths of lists should equal for comparing.')
    return [l1[x] and l2[x] for x in range(len(l1))]
def _or_iter(l1, l2):
    if len(l1) != len(l2):
        raise Exception('Lengths of lists should equal for comparing.')
    return [l1[x] or l2[x] for x in range(len(l1))]
def _not_iter(l1):
    return [not x for x in l1]


class User:
    URL = 'https://api.spotify.com/v1/'
    ME_URL = URL + 'me/'
    TRACK = 'spotify:track:'

    def __init__(self, token, token_birth):
        self.token = token
        self.token_birth = token_birth
        self.headers = {'Authorization': 'Bearer ' + self.token}
        self.headers_json = {'Authorization': 'Bearer ' + self.token,
                             'Content-Type': 'application/json'}
        self.user = requests.get(self.ME_URL, headers=self.headers).json()['id']
        self.playlists, self.pl_ids, self.pl_lens = self._get_playlists()
        self.queue = []

    def _get_playlists(self):
        """
        Get the playlists of the current user (as determined by the token)
        """
        pl_response = requests.get(self.ME_URL + 'playlists', headers=self.headers)

        playlists, pl_ids, pl_lens = [], [], []
        for playlist in pl_response.json()['items']:
            playlists.append(playlist['name'])
            pl_ids.append(playlist['id'])
            pl_lens.append(playlist['tracks']['total'])

        return playlists, pl_ids, pl_lens

    def play(self, data={}):
        """
        Plays the music. Can pass a dictionary of song URIs to create a queue
        with in the following format:
                    {"uris": ["spotify:track:<song_id>", ...]}
        If nothing is passed, the music will just play.

        Parameters:
        data - (default {}) Song URIs to be passed to create a queue
        """
        requests.put(self.ME_URL + 'player/play', headers=self.headers, data=dumps(data))

    def pause(self):
        """
        Pauses the music
        """
        requests.put(self.ME_URL + 'player/pause', headers=self.headers)

    def get_playlist_songs(self, pl_id):
        """
        Returns a list of [song, list of the artists] for each song in a
        playlist for the given user.

        Parameters:
        pl_id - The playlist id of the user to get the song data for
        """
        # Make sure the playlist name exists
        if pl_id not in self.pl_ids:
            raise Exception('Playlist ID {} not found for user {}'.format(
                pl_id, self.user))

        # Get playlist number of tracks for given playlist name
        pl_len = self.pl_lens[self.pl_ids.index(pl_id)]

        # Form URL to get song data
        url = self.URL + 'users/{}/playlists/{}/tracks'.format(self.user, pl_id)

        songs = set()
        # API only allows 100 songs at a time for some reason, so keep
        # requesting 100 until we got them all
        for offset in range(ceil(pl_len / 100)):
            params = {'offset': offset * 100}
            song_response = requests.get(url, headers=self.headers, params=params)
            song_data = song_response.json()['items']

            for song in song_data:
                songs.add((song['track']['name'],
                           tuple([data['name'] for data in song['track']['artists']]),
                           song['track']['id']))

        return songs

    @staticmethod
    def _make_mask_artists(songs, logic, filt):
        """
        A template used for filtering for artists_or and artists_and
        """
        mask = []
        for song in songs:
            # Map to lowercase, check if names given in artist list for songs
            mask.append(logic([y.lower() in map(lambda x: x.lower(), song[1])
                               for y in filt]))
        return mask

    @staticmethod
    def _make_mask_artist(songs, logic, filt):
        """
        A template used for filtering for artist_or and artist_and
        """
        mask = []
        for song in songs:
            # In lowercase, double loop to check against each artist for songs
            mask.append(any([logic([y.lower() in x.lower() for y in filt])
                             for x in song[1]]))
        return mask

    @staticmethod
    def _make_mask_song(songs, logic, compare, filt):
        """
        A tempalte used for filtering for song_exact, song_or and song_and
        """
        mask = []
        for song in songs:
            # In lowercase, look for == (exact) or 'in' the song name for songs
            mask.append(logic([compare(x.lower(), song[0].lower())
                               for x in filt]))
        return mask

    def filter_playlist(self, songs, _and=None, _or=None, _not=False, **kwargs):
        """
        Given a list of songs in the format given by get_playlist_songs, it
        will be filtered be filtered through arbitarily nested ANDs and ORs via
        dictionaries with a NOT option. It is case-insensitive. For example:

                    _or=dict(
                        song_and=['a', 'e', 'i', 'o', 'u'],
                        _and=dict(
                            artist_or=['lil', 'big'],
                            _or=dict(
                                _not=True
                                song_or=['no', 'yes']
                            )
                        )
                    )

        This will returns songs that either have every vowel in their title or
        songs that both have an artist with 'lil' or 'big' in their names or
        a song with neither 'yes' or 'no' in the title. This is a rediculous
        example, but it shows what can be done with it. Neither the _or or _and
        dictionary need to be used and the keywords can just be passed (which
        would assume _or, so _or is the default) The _not keyword is just
        switched to True for the dictionary to be inverted. If only one keyword
        needs to be inverted, wrap it in a dictionary like above. The possible
        keywords that can be used are:

            artists_and - Every element of the list must be an artist of the
                          song
            artists_or - At least one element of the list must be an artist of
                         the song
            artist_and - At least one artist of the song must have every element
                          in the list found in their name
            artist_or - At least one artist of the song must have at least one
                        element in the lsit found in their name                        
            song_exact - The song name must be exactly one of the elements in
                         the list
            song_and - The song name must have every element of the list found
                       in it
            song_or - The song name must have at least one element of the list
                      found in it

        Paramters:
        songs - The list of songs to filter
        _and - (default None) Filter dictionary, it will AND all of it's values
        _or - (default None) Filter dictionary, it will OR all of it's values
        _not - (default False) Will NOT the resulting mask. If to be applied
               to a single kwarg, wrap in an _or dict
        kwargs - The top level filtering keywords (these will be OR'd with
                 each other and the _and and _or dict if they exist)
        """
        mask = self._build_mask(songs, _and=_and, _or=_or, **kwargs)
        return set(compress(songs, mask))

    def _build_mask(self, songs, mask=None, _and=None, _or=None, _not=False,
                    or_mask=True, **kwargs):
        """
        Creates the mask used to filter a list of songs recursively. Called from
        filter_playlist.
        """
        if _or:
            or_mask = self._build_mask(songs, **_or)
        if _and:
            and_mask = self._build_mask(songs, **_and, or_mask=False)

        # Whether to OR the masks or AND them
        logic = _or_iter if or_mask else _and_iter
        # Initialize mask with Falses for OR and Trues for AND
        mask = [not or_mask] * len(songs)
        if _or:
            mask = logic(or_mask, mask)
        if _and:
            mask = logic(and_mask, mask)

        # Add artists AND
        if 'artists_and' in kwargs:
            mask = logic(mask, self._make_mask_artists(songs, all, kwargs['artists_and']))
        # Add artists OR
        if 'artists_or' in kwargs:
            mask = logic(mask, self._make_mask_artists(songs, any, kwargs['artists_or']))
        # Add artist AND
        if 'artist_and' in kwargs:
            mask = logic(mask, self._make_mask_artist(songs, all, kwargs['artist_and']))
        # Add artist OR
        if 'artist_or' in kwargs:
            mask = logic(mask, self._make_mask_artist(songs, any, kwargs['artist_or']))
        # Add song EXACT
        if 'song_exact' in kwargs:
            mask = logic(mask, self._make_mask_song(songs, any, _equiv, kwargs['song_exact']))
        # Add song AND
        if 'song_and' in kwargs:
            mask = logic(mask, self._make_mask_song(songs, all, _in, kwargs['song_and']))
        # Add Song OR
        if 'song_or' in kwargs:
            mask = logic(mask, self._make_mask_song(songs, any, _in, kwargs['song_or']))

        return _not_iter(mask) if _not else mask

    def create_queue(self, song_ids, new_queue=False, duplicate=False):
        """
        Given a list of song data, create a queue

        Parameters:
        song_ids - The song IDs to create the queue from
        new_queue - (default False) If True, will create a new queue, else it
                    will append to the previous queue
        duplicate - (default False) If True, will add duplicate songs, else not
        """
        # Remake the queue if it's a new queue
        if new_queue:
            self.queue = [self.TRACK + song_id for song_id in song_ids]
        else:
            # Else add to existing queue
            for song_id in song_ids:
                song_uri = self.TRACK + song_id
                # Don't add duplicate to queue if not wanted
                if not duplicate:
                    if song_uri not in self.queue:
                        self.queue.append(song_uri)
                else:
                    self.queue.append(song_uri)
        self.play(data={'uris': self.queue})

    def create_playlist(self, songs, name, public=True):
        """
        Creates a playlist of songs.

        Parameters:
        songs - The songs to create the 'queue' with
        name - The name of the playlist
        public - (default True) Decides whether the playlist is public (True)
                 or private (False)
        """
        # Create the playlist and store the playlist ID
        url = self.URL + 'users/{}/playlists'.format(self.user)
        data = {'name': name, 'public': public}
        pl_id = requests.post(url, headers=self.headers_json,
                              data=dumps(data)).json()['id']

        # Add new playlist to the playlist info
        self.playlists.append(name)
        self.pl_ids.append(pl_id)
        # Initialize the pl_len, length will be added in add_to_playlist
        self.pl_lens.append(0)

        # Add the songs to the playlist
        self.add_to_playlist(pl_id, songs)

    def add_to_playlist(self, pl_id, songs):
        """
        Adds songs to a playlist and updates the info on the user's playlists.
        This will add duplicates.

        Parameters:
        pl_id - The id of the playlist
        songs - The songs to add to the 'queue'
        """
        url = self.URL + 'users/{}/playlists/{}/tracks'.format(self.user, pl_id)
        data = {'uris': [self.TRACK + song[2] for song in songs]}
        requests.post(url, headers=self.headers_json, data=dumps(data))

        # Increase number of songs for this playlist by this addition
        self.pl_lens[self.pl_ids.index(pl_id)] += len(songs)

    def delete_playlist(self, pl_id):
        """
        Deletes a playlist for a user by the playlist's id

        Parameters:
        pl_id - The id of the playlist to delete
        """
        url = self.URL + 'users/{}/playlists/{}/followers'.format(
              self.user, pl_id)
        requests.delete(url, headers=self.headers)

        # Remove the playlist info
        pl_ind = self.pl_ids.index(pl_id)
        self.playlists.remove(self.playlists[pl_ind])
        self.pl_ids.remove(pl_id)
        self.pl_lens.remove(self.pl_lens[pl_ind])

    def is_expired(self):
        """
        Determines whether or not the access token as expired
        """
        return self.age() > 3500

    def age(self):
        """
        Returns how much time in seconds the token has left
        """
        return (dt.now() - self.token_birth).total_seconds()
