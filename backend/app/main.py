from fastapi import FastAPI
from .routers import  post_router,get_router


app = FastAPI()

app.include_router(router = post_router)
app.include_router(router = get_router)



@app.get("/")
def first():
    return "Welcome to ericafy"





