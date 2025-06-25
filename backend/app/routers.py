from fastapi import APIRouter, status, HTTPException, Query
from fastapi.responses import RedirectResponse
from .database import get_connection, release_connection
from .redis import get_redis_connection
from .algorithms.base62_id import base62
from .algorithms.twitter_snowflake import Snowflake
from .algorithms.hash_collision_reso import url_converter
from .models import Url, UrlCreate
from dotenv import load_dotenv
import os
from datetime import datetime
from pydantic import HttpUrl
import string
import random
from urllib.parse import urlparse

load_dotenv()

post_router = APIRouter(prefix="/api/v1/shorten", tags=["post endpoints"])
get_router = APIRouter(prefix="/api/v1/shorten", tags=["get endpoints"])

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000/")


@post_router.post("/", response_model=Url)
def get_shorturl(data: UrlCreate):
    try:
        clicks = 0
        long_url = str(data.longurl)
        created_at = datetime.now()

        sql = """
            INSERT INTO urls (
                id,
                original_url,
                short_code,
                short_url,
                clicks,
                created_at,
                method
            ) VALUES (%s, %s, %s, %s, %s, %s, %s);
        """

        tries, max_tries = 0, 7
        connection = None
        r = get_redis_connection()

        if data.method == "hash":
            while tries < max_tries:
                salt = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
                cur_code = url_converter(long_url + salt)
                cur_url = BASE_URL + cur_code
                cur_id = Snowflake().create_sequence()

                if r.exists(cur_url):
                    print(f" On try: {tries} - Cache hit: {cur_url} already exists in Redis.")
                    tries += 1
                    continue


                row_data = (
                    cur_id,
                    long_url,
                    cur_code,
                    cur_url,
                    clicks,
                    created_at,
                    data.method
                )

                try:
                    connection = get_connection()
                    with connection.cursor() as cursor:
                        cursor.execute(sql, row_data)
                        connection.commit()

                    r = get_redis_connection()
                    r.setex(cur_url,86400,long_url)
                    return Url(
                        id=cur_id,
                        longurl=long_url,
                        shortcode=cur_code,
                        shorturl=cur_url,
                        method=data.method,
                        clicks=clicks,
                        created_at=created_at,
                    )
                

                except Exception as e:
                    print(f"On try: {tries + 1} — error: {e}")
                    tries += 1
                    if connection:
                        connection.rollback()
                finally:
                    if connection:
                        release_connection(connection)

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate a unique short URL after multiple attempts."
            )

        elif data.method == "base62":
            cur_id = Snowflake().create_sequence()
            cur_code = base62(cur_id)
            cur_url = BASE_URL + cur_code

            row_data = (
                cur_id,
                long_url,
                cur_code,
                cur_url,
                clicks,
                created_at,
                data.method
            )

            try:
                connection = get_connection()
                with connection.cursor() as cursor:
                    cursor.execute(sql, row_data)
                    connection.commit()

                return Url(
                    id=cur_id,
                    longurl=long_url,
                    shortcode=cur_code,
                    shorturl=cur_url,
                    method=data.method,
                    clicks=clicks,
                    created_at=created_at
                )

            except Exception as e:
                if connection:
                    connection.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Database insert failed: {str(e)}"
                )
            finally:
                if connection:
                    release_connection(connection)

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid shortening method. Use 'hash' or 'base62'."
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during URL shortening: {str(e)}"
        )


@get_router.get("/")
def redirect_url(cururl: HttpUrl = Query(...)):
    sql = "SELECT original_url FROM urls WHERE short_url= %s"  
    connection = None

    try:
        r = get_redis_connection()
        key = str(cururl)
        value = r.get(key)
        if value:
            r.expire(key,86400)
            return value.decode()
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute(sql, (str(cururl),))
            response = cursor.fetchone()

        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shortened URL not found in the database."
            )

        r.setex(key,86400,str(response["original_url"]))
        return response["original_url"]

    except Exception as e:
        if connection:
            connection.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch original URL: {str(e)}"
        )
    finally:
        if connection:
            release_connection(connection)
