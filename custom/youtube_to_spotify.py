""" Add Youtube liked songs to a playlist in Spotify

Tasks:
Step 1. log into youtube
Step 2. Get to liked videos
Step 3. Create a new playlist
Step 4. Search for the song in spotify
Step 5. Add the song to the new playlist

API's:
Youtube API
Spotify Web API
youtube-dl library
"""

from datetime import datetime as dt

import youtube_dl

from core.spotify import Spotify
from core.youtube import Youtube


class HttpError(Exception):
    pass


class YoutubeToSpotify:
    def __init__(self):
        self.spotify = Spotify()
        self.youtube = Youtube()

    def enrich_youtube_liked_songs_with_spotify_data(self, n=50):
        """
        :param n: if None then capture entirety of users liked videos
        :return:
        """

        # Get my last n liked videos
        liked_video_data = self.youtube.get_liked_videos(n=n)

        output = {}

        for video in liked_video_data:
            id = video['id']
            youtube_url = f"https://www.youtube.com/watch?v={id}"
            video_name = video['snippet']['title']

            # Use the youtube_dl library to extract song_name and artist from the video
            video = youtube_dl.YoutubeDL({}).extract_info(youtube_url, download=False)
            song_name = video['track']
            artist = video['artist']
            if song_name is not None and artist is not None:
                # Check if a song is found on Spotify
                spotify_uri = self.spotify.get_track_uri(song_name=song_name, artist=artist)

                if spotify_uri is not None:
                    output[video_name] = {
                        # Youtube information
                        'youtube_url': youtube_url,
                        'song_name': song_name,
                        'artist': artist,

                        # Youtube information used to get the Spotify song uri
                        'spotify_uri': spotify_uri
                    }

        if len(output) > 0:
            return output

    def youtube_likes_to_spotify(self, playlist_name=None, youtube_videos_lookback=5):
        # Capture youtube likes and add them to a new playlist or an existing one if <playlist_name> exists

        playlist_id = None

        if playlist_name is not None:
            playlist_id = self.spotify.get_playlist_id(playlist_name)

            if playlist_id is None:
                print(f"Playlist with exact name: {playlist_name} not found\nA new one with this name will be created")
                playlist_id = self.spotify.create_playlist(name=playlist_name)

        if playlist_id is None:
            playlist_name = "_new_{:%Y%m%d_%H%M}".format(dt.today())
            print(f"A [laylist will be created with this name: {playlist_name}")
            playlist_id = self.spotify.create_playlist(name=playlist_name)

        song_data = self.enrich_youtube_liked_songs_with_spotify_data(n=youtube_videos_lookback)

        uris = []
        for song_name, song in song_data.items():
            uris.append(song['spotify_uri'])

        if len(uris) == 0:
            return

        response_json = self.spotify.add_song_to_playlist(playlist_id=playlist_id, uri=uris)

        return response_json


if __name__ == "__main__":
    yts = YoutubeToSpotify()
    yts.youtube_likes_to_spotify(youtube_videos_lookback=10)
