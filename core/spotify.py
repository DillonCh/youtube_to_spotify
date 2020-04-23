import os
import json
import requests

from core.utils import HttpError, get_json

SECRETS_PATH = "./config/spotify_secret.json"
SECRETS_TOKEN_NAME = 'spotify_token'
SECRETS_USER_ID_NAME = 'spotify_user_id'


class Spotify:
    def __init__(self):
        # Assign the file path
        self.secrets_path = SECRETS_PATH

        # Get the API key and USER ID
        self.secrets_json = self.get_secrets_json()
        self.token = self.secrets_json[SECRETS_TOKEN_NAME]
        self.user_id = self.secrets_json[SECRETS_USER_ID_NAME]

    def get_secrets_json(self):
        print(os.path.abspath(self.secrets_path))
        data = get_json(self.secrets_path)
        return data

    # Step 3. Create a new playlist
    def create_playlist(self, name=None):
        # Source: https://developer.spotify.com/documentation/web-api/reference-beta/#endpoint-create-playlist

        if name is None:
            name = "_new_playlist_spotify_api_python"

        # To create a playlist the Spotify server as per the docs expects a json 'Request Body' with this structure:
        request_body = json.dumps({
            "name": name,
            "description": "All liked youtube videos",
            "public": True
        })

        # Query 'Endpoint'
        # Note that there are some required scopes for this endpoint
        endpoint = f"https://api.spotify.com/v1/users/{self.user_id}/playlists"

        # Submit the HTTP request and get the response
        response = requests.post(
            url=endpoint,
            data=request_body,
            json=None,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}"
            }
        )

        self._validate_response(response)
        response_json = response.json()

        # Playlist ID - this will allow us to add specific songs to the playlist
        return response_json['id']

    # Step 4. Search for the song in Spotify
    def get_track_uri(self, song_name, artist):
        # Source: https://developer.spotify.com/documentation/web-api/reference-beta/#endpoint-search
        # Source: https://developer.spotify.com/documentation/web-api/reference-beta/#endpoint-get-track

        # Query 'Endpoint'
        endpoint = "https://api.spotify.com/v1/search"

        # Build the song query string
        q = "?q=track:{}+artist:{}&type=track".format(
            song_name.replace(' ', '%20'),
            artist.replace(' ', '%20')
        )

        url = endpoint + q

        response = requests.get(
            url=url,
            headers={
                "Authorization": f"Bearer {self.token}"
            }
        )

        self._validate_response(response)
        response_json = response.json()

        # Get all the songs from the response
        songs = response_json["tracks"]["items"]

        # Get only the first song from the response
        if len(songs) > 0:
            song = songs[0]

            # Return the Spotify song URI
            return song['uri']

    # Step 5. Add the song to the new playlist
    def add_song_to_playlist(self, playlist_id, uri):
        # https://developer.spotify.com/documentation/web-api/reference-beta/#endpoint-add-tracks-to-playlist

        if type(uri) in (list, tuple):
            uri = "%2C".join(uri)  # '%2C' represents ',' here

        endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?uris={uri}"

        # Submit the HTTP request and get the response
        response = requests.post(
            url=endpoint,
            json=None,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}"
            }
        )

        self._validate_response(response)
        response_json = response.json()
        return response_json

    def get_user_playlists(self):
        # Get all the current users playlist data
        endpoint = "https://api.spotify.com/v1/me/playlists"
        response = requests.get(
            url=endpoint,
            headers={
                "Authorization": f"Bearer {self.token}"
            }
        )

        self._validate_response(response)
        response_json = response.json()
        return response_json

    def get_playlist_id(self, playlist_name):
        # Get the playlist id of an existing playlist if one with this exact name already exists

        if not isinstance(playlist_name, str):
            raise ValueError("Expected playlist_name of type str")

        user_playlists_raw = self.get_user_playlists()
        user_playlists = {}

        for playlist in user_playlists_raw['items']:
            user_playlists[playlist['name']] = playlist['id']

        playlist_id = user_playlists.get(playlist_name)

        return playlist_id

    @staticmethod
    def _validate_response(response):
        # Check if a valid response was received
        if not response:
            raise HttpError(response.json()['error'])
