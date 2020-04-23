import unittest

from core.spotify import Spotify


class TestSpotify(unittest.TestCase):
    def test_get_spotify_uri(self):
        song_uri = Spotify().get_track_uri("come around me", "justin")
        # todo: this uri is not constant. Find something that is constant
        self.assertEqual(song_uri, "spotify:track:3e2VVyqCmnTXl0bBfgQgBJ")
