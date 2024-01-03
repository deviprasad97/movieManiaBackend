from flask import jsonify, request, abort
from models import MovieCollection
from auth import token_required
from utils import validate_input
import json

movie_collection = MovieCollection()

def configure_routes(app):
    @app.route('/PutMovieCollection', methods=['POST'])
    @token_required
    def add_movie():
        data = request.json
        validate_input(data)  # Assuming validate_input is a function you've created in utils.py
        result = movie_collection.add(data)
        return jsonify(result), 201

    @app.route('/RemoveMovieCollection', methods=['DELETE'])
    @token_required
    def remove_movie():
        aid = request.args.get('aid')
        movieid = request.args.get('movieid')
        validate_input({'aid': aid, 'movieid': movieid})
        result = movie_collection.delete(aid, movieid)
        return jsonify(result), 204

    @app.route('/ListMovieCollection', methods=['GET'])
    @token_required
    def list_movies():
        aid = request.args.get('aid')
        page = int(request.args.get('page', 0))
        limit = int(request.args.get('limit', 10))
        validate_input({'aid': aid, 'page': page, 'limit': limit})
        result, last_evaluated_key = movie_collection.list(aid, page, limit)
        return jsonify(result), 200
