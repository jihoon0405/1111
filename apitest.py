from flask import Flask, render_template, jsonify
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import random
import requests
from bs4 import BeautifulSoup

# 현재 파일이 위치한 디렉터리 경로
current_directory = os.path.dirname(os.path.abspath(__file__))

# Flask 애플리케이션 설정
app = Flask(__name__, template_folder=current_directory)

# Spotify API 클라이언트 정보 설정
client_id = '10037d98aae94900a5a98d844b1cb6be'
client_secret = '6ef2e814a7114892b9d0daf12079d950'

# Spotify API 인증
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

def get_tracks(genre_list, limit=15):
    all_tracks = []
    
    for genre, is_popular in genre_list:
        try:
            offset = random.randint(0, 999)
            results = sp.search(q=f'genre:{genre}', type='track', limit=50, offset=offset)
            tracks = results['tracks']['items']
            
            if is_popular:
                filtered_tracks = [{
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'album_image': track['album']['images'][0]['url'],
                    'popularity': track['popularity'],
                    'genre': genre
                } for track in tracks if track['popularity'] <= 55]
            else:
                filtered_tracks = [{
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'album_image': track['album']['images'][0]['url'],
                    'popularity': track['popularity'],
                    'genre': genre
                } for track in tracks if track['popularity'] >= 50]
            
            all_tracks.extend(filtered_tracks)
        except Exception as e:
            print(f"Error fetching tracks for genre {genre}: {e}")

    return random.sample(all_tracks, min(len(all_tracks), limit))

@app.route('/')
def index():
    return render_template('test.html')

@app.route('/update_tracks')
def update_tracks():
    genres = [
        ("lo-fi", False),
        ("ambient", False),
        ("experimental", False),
        ("post-rock", False),
        ("pop", True),
        ("rock", True),
        ("hip-hop", True),
        ("dance", True),
        ("k-pop", True)
    ]
    track_list = get_tracks(genres, limit=15)
    return jsonify(track_list)

@app.route('/chart_<int:top_n>.html')
def chart(top_n):
    if top_n not in [10, 100]:
        return "Invalid chart request", 400
    
    def crawl_melon():
        headers = {
            'User-Agent': 'Mozilla/5.0'
        }
        url = 'https://www.melon.com/chart/index.htm'
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        songs = soup.select('div.service_list_song table tbody tr')
        return songs

    def generate_chart_html(songs, top_n=100):
        html_content = '<table><tbody>'
        for idx, song in enumerate(songs[:top_n], 1):
            title = song.select_one('div.ellipsis.rank01 span a').text.strip()
            artist = song.select_one('div.ellipsis.rank02 span').text.strip()
            html_content += f'<tr><td>{idx}</td><td>{title}</td><td>{artist}</td></tr>'
        html_content += '</tbody></table>'
        return html_content

    songs = crawl_melon()
    chart_html = generate_chart_html(songs, top_n=top_n)
    return chart_html

if __name__ == '__main__':
    app.run(debug=True, port=5000)  # 포트를 적절히 설정
