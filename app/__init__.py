from flask import Flask
from config import Config
from flask_redis import FlaskRedis
import os
import redis 

app = Flask(__name__)
app.config.from_object(Config)
app.config["DEBUG"] = True
redis_client = redis.from_url(os.environ.get("REDIS_URL"))

from app import routes
