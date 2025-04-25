# CJW
# User.py
# 时间：2025-04-24 20:50
import math
import random
from collections import defaultdict

from fastapi import APIRouter, Request, Form
from starlette.templating import Jinja2Templates
from .models import User

user = APIRouter()

template = Jinja2Templates(directory="templates")


@user.get("/get")
async def get_user(request: Request):
    user = await User.all()
    for u in user:
        print(u.to_json())
    return template.TemplateResponse("login.html", {"request": request})


@user.get("/get/{id}")
async def get_byid(id: int, request: Request):
    user = await User.filter(id=id)
    for u in user:
        print(u.to_json())
    return template.TemplateResponse("login.html", {"request": request})


@user.post("/")
async def set_user(request: Request):
    # User.create(request.form)
    return {"message": "success"}


@user.put("/{id}")
async def upd_user(id: int, request: Request):
    # user = User.fliter_by_id(id).update(request.form)
    return template.TemplateResponse("login.html", {"request": request})


@user.get("/get_name/{id}")
async def get_name_byid(id: int, request: Request):
    # user = User.fliter_by_id(id)
    # print(user.name)
    return template.TemplateResponse("1.html", {"request": request})
