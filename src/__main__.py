import json
import os
import spotipy
import keyboard


SPOTIFY_SCOPES = [
  "user-read-playback-state",
  "user-modify-playback-state",
  "user-read-currently-playing"
]
SPOTIFY_REDIRECT_URI = 'http://127.0.0.1:8080/callback'


def read_config() -> any:
  has_user_config = os.path.exists('user_config.json')

  with open('user_config.json' if has_user_config else 'config.json', 'r') as file:
    data = json.load(file)

  return data

def create_spotify_object(creds) -> spotipy.Spotify:
  try:
    client_id, client_secret = creds["spotify_client_id"], creds["spotify_client_secret"]

    auth_manager = spotipy.oauth2.SpotifyOAuth(
      client_id=client_id,
      client_secret=client_secret,
      redirect_uri=SPOTIFY_REDIRECT_URI,
      scope=" ".join(SPOTIFY_SCOPES),
      cache_path=".spotify_cache"
    )

    spotify = spotipy.Spotify(auth_manager=auth_manager)

    return spotify
  except spotipy.SpotifyException as e:
    return None

def hook_keyboard(spotify, cfg) -> None:
  callback = lambda event: handle_keyboard_events(event, spotify, cfg)
  
  keyboard.hook(callback)
  keyboard.wait()

def handle_keyboard_events(event, spotify, cfg) -> None:
  volume_up_key, volume_down_key = cfg["controls"]["volume_up"], cfg["controls"]["volume_down"]
  volume_up_amt, volume_down_amt = cfg["volume_up_percent"], cfg["volume_down_percent"]

  if event.event_type != 'down':
    return

  if event.name == volume_up_key:
    change_volume(spotify, volume_up_amt)
  elif event.name == volume_down_key:
    change_volume(spotify, 0 - volume_down_amt)

def change_volume(spotify, diff):
  try:
    playback = spotify.current_playback()
    
    if playback is None:
      return
    
    current_volume = playback['device']['volume_percent']
    new_volume = max(0, min(100, current_volume + diff))

    spotify.volume(new_volume)
  except spotify.SpotifyException:
    spotify = create_spotify_object()
    change_volume(spotify, diff)


if __name__ == "__main__":
  try:
    config = read_config()
    credentials, controls = config["credentials"], config["controls"]

    spotify = create_spotify_object(credentials)
    hook_keyboard(spotify, config)
  except Exception as e:
    print(e)