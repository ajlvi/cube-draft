import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
	REDIS_URL = "redis://h:p18ca4e75cfaba7dea7028f639f54e15682117493b6cd9a2982ec2ed2217e751b@ec2-52-70-215-224.compute-1.amazonaws.com:29529"