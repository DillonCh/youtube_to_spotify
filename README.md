*This is my first README*
**This text should be in bold**
This text should be normal

1. this is a numbered...
2. list

* this should be a bullet list
* and this

[] this should be an unfilled task box
[x] this sould be a filled task box


Configuration files that you must create first:
1. Spotify API token and Spotify user ID
	- path: ./core_config/spotify_secret.json
	- contents: {"spotify_token":"<your spotify_token here>", "spotify_user_id":"<your spotify_user_id here>"}
	- source: https://developer.spotify.com/console/post-playlists/

2. YouTube OAuth secret
	- path: ./core_config/youtube_secret.json
	- contents: you can download the entire file from the source, there is no need to create this yourself
	- source: https://console.developers.google.com/apis/dashboard > OAuth 2.0 Client IDs > my_project_name > download. If you don't have a project set up you can do this using the 'create credential's button on the dashboard then return to the mentioned steps.

3. YouTube API token
	- path: ./core_config/youtube_api_key.json
	- contents: {"api_key":"<your api key here>"}
	- source: https://console.developers.google.com/apis/credentials?project=my-spotify-python-project > API keys > Key. If you don't have an API key set up you can do this using the 'create credential's button on the dashboard then return to the mentioned steps.


