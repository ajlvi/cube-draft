from flask import Flask
from config import Config
from flask_redis import FlaskRedis

app = Flask(__name__)
app.config.from_object(Config)
app.config["DEBUG"] = True
redis_client = FlaskRedis(app)

from app import routes
