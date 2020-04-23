"""
I prefer this since instead of using all the fancy google-python stuff and having to learn that,
all we do is instead use the authenitifcation stuff then resume as normal with a http request
i.e. using the 'requests' library

"""

import os
import json
import requests
from math import ceil

from core.utils import HttpError, get_json

import google_auth_oauthlib.flow

MAX_RESULTS_PER_PAGE = 50  # determine by the YouTube API
API_KEY_PATH = './config/youtube_api_key.json'
SECRETS_PATH = "./config/youtube_secret.json"
SECRETS_API_NAME = 'api_key'


class Youtube:
    def __init__(self):
        # Assign the file paths
        self.secrets_path = SECRETS_PATH
        self.api_key_path = API_KEY_PATH

        # Get the OAuth credentials
        self.credentials = self.get_youtube_credentials()
        self.token = self.credentials.token

        # Get the API key
        self.secrets_json = self.get_secrets_json()
        self.api_key = self.secrets_json[SECRETS_API_NAME]

        # Other settings
        self.max_results_per_page = MAX_RESULTS_PER_PAGE

    def get_secrets_json(self):
        data = get_json(self.api_key_path)
        return data

    def get_youtube_credentials(self):
        # Copied from Youtube API docs:
        # https://developers.google.com/youtube/v3/code_samples/code_snippets?apix=true&apix_params=%7B%22part%22%3A%22snippet%2CcontentDetails%2Cstatistics%22%2C%22myRating%22%3A%22like%22%7D
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

        # Get credentials and create an API client
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            self.secrets_path, scopes)
        credentials = flow.run_console()

        return credentials

    def template(self):
        request_body = json.dumps({
            "name": "new_name",
            "description": "All liked youtube videos",
            "public": True
        })

        # Query 'Endpoint'
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
        return response_json

    def _get_liked_videos_by_page(self, results=5, page_token=None):
        """ Source: https://developers.google.com/youtube/v3/docs/videos/list?apix=true

        HTTP request:
            GET https://www.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails%2Cstatistics&maxResults=50&myRating=like&pageToken=2&key=[YOUR_API_KEY] HTTP/1.1

            Authorization: Bearer [YOUR_ACCESS_TOKEN]
            Accept: application/json

        """

        if results > self.max_results_per_page:
            raise ValueError(f"Limit {self.max_results_per_page} results, you passed {results}. "
                             f"Loop through <pages> in segments of {self.max_results_per_page}")

        # Build the URL
        url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails%2Cstatistics&maxResults={results}&myRating=like"

        if page_token is not None:
            url += f"&pageToken={page_token}"

        url += f"&key={self.api_key}"

        response = requests.get(
            url=url,
            headers={
                "Accept": "application/json",  # could be "Content-Type": ...
                "Authorization": f"Bearer {self.token}"
            }
        )

        self._validate_response(response)
        response_json = response.json()

        return response_json

    def get_liked_videos_count(self):
        # Return the number of liked videos for the user
        # This is hacky since I also return the video data for 1 video
        return self._get_liked_videos_by_page(1)['pageInfo']['totalResults']

    def get_liked_videos(self, n=None):
        """ If n=None then get the entire list
        We can only capture 50 (or self.max_results_per_page) items at a time and they are separated by 'pages'.
        A page is identified by it's pageToken, and each response may provide:
            nextPageToken	string
            prevPageToken	string
        """

        if n is None:
            # If n=None then get the entire list
            n = self.get_liked_videos_count()

        total_pages = ceil(n / self.max_results_per_page)

        output = []
        next_page_token = None

        for page in range(1, total_pages + 1):
            # If n is not a multiple of self.max_results_per_page then the final page will only be part filled
            results_to_get = min(self.max_results_per_page, n)

            response = self._get_liked_videos_by_page(results=results_to_get, page_token=next_page_token)

            next_page_token = response.get('nextPageToken')
            output += response['items']

        return output

    def get_playlists(self):
        """
        GET https://www.googleapis.com/youtube/v3/playlists?part=snippet%2CcontentDetails&maxResults=25&mine=true&key=[YOUR_API_KEY] HTTP/1.1

        Authorization: Bearer [YOUR_ACCESS_TOKEN]
        Accept: application/json
        """

        # Build the URL
        url = f"https://www.googleapis.com/youtube/v3/playlists?part=snippet%2CcontentDetails&maxResults=50&mine=true"
        url += f"&key={self.api_key}"

        response = requests.get(
            url=url,
            headers={
                "Accept": "application/json",  # could be "Content-Type": ...
                "Authorization": f"Bearer {self.token}"
            }
        )

        self._validate_response(response)
        response_json = response.json()

        return response_json

    def add_video_to_playlist(self, playlist_id, video_id):
        """
        If video_id is a list/tuple then attempt to add each video to the playlist individually

        Source: https://developers.google.com/youtube/v3/docs/playlistItems/insert
        """
        if not isinstance(playlist_id, str):
            raise TypeError(f"playlist_id must be a str type. You passed a {type(playlist_id)}")

        if type(video_id) in (tuple, list):
            for single_video_id in video_id:
                self.add_video_to_playlist(playlist_id, single_video_id)
                print(f"Done: {single_video_id}")

        # Build the URL
        url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&key={self.api_key}"

        request_body = json.dumps({
          "snippet": {
            "playlistId": playlist_id,
            "position": 0,
            "resourceId": {
              "kind": "youtube#video",
              "videoId": video_id
            }
          }
        })

        response = requests.post(
            url=url,
            data=request_body,
            headers={
                "Accept": "application/json",  # could be "Content-Type": ...
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
        )

        self._validate_response(response)
        response_json = response.json()

        return response_json

    @staticmethod
    def _validate_response(response):
        # Check if a valid response was received
        if not response:
            raise HttpError(response.json()['error'])


if __name__ == "__main__":
    x = Youtube()
    y = x._get_liked_videos_by_page()
    print(y)
