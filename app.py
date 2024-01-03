from flask import Flask
from routes import configure_routes
from blu_ray_routes import configure_blu_ray_routes

app = Flask(__name__)
configure_routes(app)
configure_blu_ray_routes(app)

if __name__ == '__main__':
     app.run(host="0.0.0.0", debug=True)  # Set debug to False in production