# app.py - arquivo principal do FastAPI para a orquestração do suporte

from fastapi import FastAPI
from ia_suporte.api.router import router

app = FastAPI()
app.include_router(router)