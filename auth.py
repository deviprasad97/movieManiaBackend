from functools import wraps
from flask import request, jsonify
import os

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token != os.environ.get('API_TOKEN'):
            return jsonify({'message': 'Invalid or missing token'}), 403
        return f(*args, **kwargs)
    return decorated_function
