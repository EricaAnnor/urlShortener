from pydantic import BaseModel,HttpUrl,Field
from enum import Enum
from datetime import datetime 
from typing import Optional



class Method(str,Enum):
    Base62 = "base62"
    Hash = "hash"


class UrlCreate(BaseModel):
    longurl:HttpUrl
    method:Method

class Url(BaseModel):

    id:Optional[int] = None
    longurl:HttpUrl
    shortcode:str
    shorturl:HttpUrl
    method:Method
    clicks:int = Field(default=0)
    created_at:datetime = Field(default = datetime.now())
    




