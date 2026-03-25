from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

OMDB_KEY = os.environ.get('OMDB_KEY', '2110d962')
TMDB_KEY = os.environ.get('TMDB_KEY', '7582a4881cf15c6bd1e000371e4dd3d4')

@app.route('/')
def index():
    return 'Film Kulübü Proxy çalışıyor!'

@app.route('/search')
def search():
    q = request.args.get('q', '')
    if not q:
        return jsonify({'Search': [], 'Response': 'False'})
    
    results = []
    seen = set()
    
    # OMDb araması
    try:
        resp = requests.get('https://www.omdbapi.com/', params={'apikey': OMDB_KEY, 's': q, 'type': 'movie'}, timeout=5)
        for f in resp.json().get('Search', []):
            if f['imdbID'] not in seen:
                seen.add(f['imdbID'])
                results.append(f)
    except:
        pass
    
    # TMDB araması (Türkçe dahil)
    try:
        resp2 = requests.get('https://api.themoviedb.org/3/search/movie', params={'api_key': TMDB_KEY, 'query': q, 'language': 'tr-TR'}, timeout=5)
        for f in resp2.json().get('results', [])[:8]:
            try:
                ext = requests.get(f'https://api.themoviedb.org/3/movie/{f["id"]}/external_ids', params={'api_key': TMDB_KEY}, timeout=3)
                imdb_id = ext.json().get('imdb_id')
                if imdb_id and imdb_id not in seen:
                    seen.add(imdb_id)
                    poster = f'https://image.tmdb.org/t/p/w92{f["poster_path"]}' if f.get('poster_path') else 'N/A'
                    results.append({'Title': f.get('title', ''), 'Year': f.get('release_date', '')[:4], 'imdbID': imdb_id, 'Poster': poster, 'Type': 'movie'})
            except:
                pass
    except:
        pass
    
    return jsonify({'Search': results[:10], 'Response': 'True'})

@app.route('/detail')
def detail():
    mid = request.args.get('id', '')
    if not mid:
        return jsonify({'Response': 'False'})
    resp = requests.get('https://www.omdbapi.com/', params={'apikey': OMDB_KEY, 'i': mid}, timeout=5)
    return jsonify(resp.json())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
