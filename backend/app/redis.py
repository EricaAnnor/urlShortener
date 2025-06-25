import redis
import os
from dotenv import load_dotenv

load_dotenv()

def get_redis_connection():

    connection = redis.Redis(host = os.getenv("REDIS_HOST"),port = os.getenv("REDIS_PORT"),db = 0, decode_responses = True)

    return connection 