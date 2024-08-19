from flask import jsonify, request, abort
from models import MovieCollection
from auth import token_required
from utils import validate_input
import json
import requests

movie_collection = MovieCollection()

TMDB_API_KEY = "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI4NDUzN2ZiN2U0N2VlMDI2Y2VhMTMwN2NmZTc2MzkzOSIsIm5iZiI6MTcyNDAzMDExNC4xMDYwNDYsInN1YiI6IjY1ODY0MGQ1NWFiYTMyNjc1OWI5MDQwNiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.1oXbMuFG14rd0WYhBRQ9ZjOUx95QzCe-PQT5cY5Mmvk"
headers = {
    "accept": "application/json",
    "Authorization": TMDB_API_KEY
}
def configure_tmdb_routes(app):
    @app.route('/GetRelatedVideos', methods=['POST'])
    @token_required
    def getRelatedVideosFromTMDB():
        data = request.get_json()
        try:
            content_id = data['content_id']
            content_type = data['content_type']
            if content_type not in ['movie', 'tv']:
                abort(400, description="Invalid content type")
            elif content_type =='movie':
                response = requests.get(f'https://api.themoviedb.org/3/movie/{content_id}/videos?language=en-US', headers=headers)
            elif content_type == 'tv':
                response = requests.get(f'https://api.themoviedb.org/3/tv/{content_id}/videos?language=en-US', headers=headers)
        except requests.exceptions.RequestException as e:
            return jsonify({'error': str(e)}), 500

        return jsonify(response.json()), 201

    @app.route('/GetContentDetails', methods=['POST'])
    @token_required
    def getContentDetailsFromTMDB():
        data = request.get_json()
        try:
            content_id = data['content_id']
            content_type = data['content_type']
            if content_type not in ['movie', 'tv']:
                abort(400, description="Invalid content type")
            elif content_type =='movie':
                response = requests.get(f'https://api.themoviedb.org/3/movie/{content_id}?language=en-US', headers=headers)
            elif content_type == 'tv':
                response = requests.get(f'https://api.themoviedb.org/3/tv/{content_id}?language=en-US', headers=headers)
        except requests.exceptions.RequestException as e:
            return jsonify({'error': str(e)}), 500

        return jsonify(response.json()), 201
    
    @app.route('/GetRelatedClips', methods=['POST'])
    @token_required
    def getRelatedClipsFromTMDB():
        data = request.get_json()
        try:
            content_id = data['content_id']
            content_type = data['content_type']
            if content_type not in ['movie', 'tv']:
                abort(400, description="Invalid content type")
            elif content_type =='movie':
                response = requests.get(f'https://api.themoviedb.org/3/movie/{content_id}/videos?language=en-US', headers=headers)
            elif content_type == 'tv':
                response = requests.get(f'https://api.themoviedb.org/3/tv/{content_id}/videos?language=en-US', headers=headers)
        except requests.exceptions.RequestException as e:
            return jsonify({'error': str(e)}), 500

        return jsonify(response.json()), 201
    
    @app.route('/GetReviews', methods=['POST'])
    @token_required
    def getReviewsFromTMDB():
        data = request.get_json()
        
        try:
            content_id = data['content_id']
            content_type = data['content_type']
            if content_type not in ['movie', 'tv']:
                abort(400, description="Invalid content type")
            elif content_type =='movie':
                response = requests.get(f'https://api.themoviedb.org/3/movie/{content_id}/reviews?language=en-US', headers=headers)
            elif content_type == 'tv':
                response = requests.get(f'https://api.themoviedb.org/3/tv/{content_id}/reviews?language=en-US', headers=headers)
        except requests.exceptions.RequestException as e:
            return jsonify({'error': str(e)}), 500
        print(response.json())
        return jsonify(response.json()), 201