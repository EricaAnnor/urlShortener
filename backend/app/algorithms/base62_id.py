from .twitter_snowflake import Snowflake
import os
from dotenv import load_dotenv


load_dotenv()

conversion = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

def base62(cur_id):


    converted_id = ''

    while cur_id > 0:

        cur = cur_id % 62 
        converted_id += conversion[cur]

        cur_id //= 62

    
    return  converted_id[::-1]












