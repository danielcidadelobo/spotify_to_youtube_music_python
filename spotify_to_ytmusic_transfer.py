import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, HttpError
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from tqdm import tqdm

SPOTIFY_CREDENTIALS_FILE = "spotify_credentials.json"

def save_spotify_credentials(credentials):
    with open(SPOTIFY_CREDENTIALS_FILE, "w") as f:
        json.dump(credentials, f)

def load_spotify_credentials():
    if os.path.exists(SPOTIFY_CREDENTIALS_FILE):
        with open(SPOTIFY_CREDENTIALS_FILE, "r") as f:
            return json.load(f)
    return None

def authenticate_spotify():
    credentials = load_spotify_credentials()
    if not credentials:
        client_id = input("Insira o seu Spotify Client ID: ").strip()
        client_secret = input("Insira o seu Spotify Client Secret: ").strip()
        credentials = {"client_id": client_id, "client_secret": client_secret}
        save_spotify_credentials(credentials)
    
    auth_manager = SpotifyOAuth(
        client_id=credentials["client_id"],
        client_secret=credentials["client_secret"],
        redirect_uri="http://localhost:8887/callback",
        scope="playlist-read-private"
    )

    return spotipy.Spotify(auth_manager=auth_manager)

def authenticate_youtube():
    SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('youtube', 'v3', credentials=creds)

def spotify_playlist_exists(sp, playlist_url):
    try:
        playlist_id = playlist_url.split("playlist/")[-1].split("?")[0]
        sp.playlist(playlist_id)
        return True
    except spotipy.exceptions.SpotifyException:
        return False

def youtube_playlist_exists(youtube, playlist_url):
    try:
        playlist_id = playlist_url.split("list=")[-1].split("&")[0]
        response = youtube.playlists().list(part="id", id=playlist_id).execute()
        return bool(response.get("items"))
    except HttpError:
        return False

def get_valid_spotify_url(sp):
    while True:
        url = input("Insira a URL da playlist do Spotify: ").strip()
        if "open.spotify.com/playlist/" in url and spotify_playlist_exists(sp, url):
            return url
        print("Erro: A URL fornecida não é válida ou a playlist não existe. Tente novamente.")

def get_valid_youtube_url(youtube):
    while True:
        url = input("Insira a URL da playlist do YouTube Music: ").strip()
        if "music.youtube.com/playlist?list=" in url and youtube_playlist_exists(youtube, url):
            return url
        print("Erro: A URL fornecida não é válida ou a playlist não existe. Tente novamente.")

def get_playlist_tracks(sp, playlist_url):
    playlist_id = playlist_url.split("playlist/")[-1].split("?")[0]
    results = sp.playlist_tracks(playlist_id)
    tracks = []
    count = 0
    while results:
        tracks += [f"{count + i + 1}. {t['track']['name']} - {t['track']['artists'][0]['name']}" for i, t in enumerate(results['items'])]
        count += len(results['items'])
        results = sp.next(results) if results.get('next') else None

    return tracks

def create_youtube_playlist(youtube, title, description=""):
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {"title": title, "description": description},
            "status": {"privacyStatus": "private"}
        }
    )
    return request.execute().get('id')

def add_tracks_to_youtube_playlist(youtube, playlist_id, tracks, start_index):
    batch_size = 5
    failed_tracks = []
    try:
        i=start_index
        for i in tqdm(range(start_index, len(tracks), batch_size), desc="Transferindo músicas"):
            batch = tracks[i:i+batch_size]
            video_ids = []
            for track in batch:
                search_response = youtube.search().list(q=track.split(". ")[-1] + " audio", part='id', maxResults=1, type='video').execute()
                if search_response['items']:
                    video_ids.append(search_response['items'][0]['id']['videoId'])
                else:
                    failed_tracks.append(track)
            
            for video_id in video_ids:
                youtube.playlistItems().insert(
                    part="snippet",
                    body={"snippet": {"playlistId": playlist_id, "resourceId": {"kind": "youtube#video", "videoId": video_id}}}
                ).execute()
    except HttpError as e:
        if e.resp.status == 403 and 'quotaExceeded' in str(e):
            print("Erro: Limite de cota da API do YouTube excedido. Musicas nao transferidas serao guardadas num ficheiro txt.")
        else:
            raise e
    finally:
        return failed_tracks + tracks[i:]

def transfer_playlist_to_youtube():
    sp = authenticate_spotify()
    youtube = authenticate_youtube()
    spotify_playlist_url = get_valid_spotify_url(sp)
    tracks = get_playlist_tracks(sp, spotify_playlist_url)
    
    print("Musicas na playlist do Spotify:")
    for track in tracks:
        print(track)
    
    while True:
        try:
            start_num = int(input("A partir de qual musica voce quer comecar a transferir? (Digite o numero): "))
            if 0 <= start_num -1  < len(tracks):
                break
            else:
                print(f"Por favor, insira um número entre 1 e {len(tracks)}.")
        except ValueError:
            print("Por favor, insira um número válido.")
    
    action = input("Criar nova playlist (c) ou adicionar a existente (a)?: ").lower()
    if action == 'a':
        youtube_url = get_valid_youtube_url(youtube)
        playlist_id = youtube_url.split("list=")[-1].split("&")[0]
    else:
        playlist_name = input("Nome da nova playlist: ")
        playlist_id = create_youtube_playlist(youtube, playlist_name)
    
    failed_tracks = add_tracks_to_youtube_playlist(youtube, playlist_id, tracks, start_index)
    
    if failed_tracks:
        file_path = input("Onde deseja guardar o ficheiro txt com as músicas nao transferidas? (Digite o caminho completo): ").strip() + "/unsaved_musics.txt"
        with open(file_path, "w") as f:
            f.write("\n".join(failed_tracks))
        print(f"Ficheiro Guardado em {file_path}.")
    print("Transferencia concluida!")

transfer_playlist_to_youtube()