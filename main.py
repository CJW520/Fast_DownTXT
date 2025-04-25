import asyncio
import datetime
import functools
import re
from http.client import HTTPException

import aiohttp
import cn2an
import requests
import sqlalchemy  # SQL工具包和ORM
from databases import Database  # 异步数据库库
from fastapi import FastAPI, Request, Cookie, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from lxml import html
from pydantic import BaseModel  # 数据验证和设置管理
from sqlalchemy import Column, Integer, String, select, insert, update
# from fastapi_sessions import SessionMiddleware
import uvicorn
import tkinter as tk
from tkinter import filedialog
import os

from starlette.authentication import AuthenticationBackend, AuthCredentials, SimpleUser
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, RedirectResponse

from blueprints.User import user

# region 数据库配置
# 定义SQLite数据库连接URL，数据库文件将保存在当前目录下的test.db文件中
DATABASE_URL = "sqlite:///./Db.sqlite"

# 创建Database实例，用于异步数据库操作
database = Database(DATABASE_URL, timeout=90)
# 创建SQLAlchemy元数据对象，用于管理表结构
metadata = sqlalchemy.MetaData()

# 定义items表结构

items = sqlalchemy.Table(
    "TXT",  # 表名
    metadata,  # 关联的元数据对象
    # 定义列
    Column("ID", Integer, primary_key=True),  # 主键ID
    Column("NAME", String),  # 名称字段
    Column("TITLE", String),
    Column("TXT", String),  # 描述字段(可选)
    Column("NUMS", Integer)
)
# 创建SQLAlchemy引擎实例
# connect_args={"check_same_thread": False} 允许不同线程使用同一个连接(SQLite需要)
engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": True}, echo=True
)

# 根据定义的表结构在数据库中创建实际表
metadata.create_all(engine)




class TxtItem(BaseModel):
    id: int
    name: str
    title: str
    txt: str
    nums: int


htmls = ''
names = ''
snum = ''
txtlist = []
lists = []
listError = []
# endregion

# http://127.0.0.1:88/1

# app = FastAPI(on_startup=[database.connect], on_shutdown=[database.disconnect])  #  , docs_url=None, redoc_url=None, openapi_url=None)



app = FastAPI(  on_startup=[database.connect],
              on_shutdown=[database.disconnect])  # , docs_url=None, redoc_url=None, openapi_url=None)

# os.makedirs("./static", exist_ok=True)
# os.makedirs("./templates", exist_ok=True)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(user, prefix="/users", tags=["users"])



# app.add_middleware(
#     SessionMiddleware,
#     secret_key="cjw74520cjw74520cjw74520cjw74520cjw74520cjw74520",
#     session_cookie="session_cookie",
#     same_site="lax",  # 跨站请求时，只发送 cookie 给同站点的请求
# )
# app = FastAPI()
from functools import wraps


# region  在 FastAPI 启动时注册事件
# @app.middleware("http")
# async def redirect_middleware(request: Request, call_next):
#     print(f"访问路径: {request.url.path}")
#     print(f"携带Cookies: {request.cookies}")
#     print( request )
#     try:
#         if hasattr(request, "session"):
#             print(request.session)
#     except Exception:
#         print("Session为NONE")
#     # 排除首页、静态文件和 favicon.ico
#     if request.url.path in ["/", "/favicon.ico"] or request.url.path.startswith("/static/"):
#         print("跳过静态文件或首页")
#         return await call_next(request)
#
#     # 检查 Cookie
#     if "visited" not in request.cookies:
#         print("首次访问，设置Cookie")
#         response = RedirectResponse(url="/")
#         response.set_cookie(
#             key="visited",
#             value="1",
#             path="/",
#             max_age=3600,
#             httponly=True,
#             secure=False,
#             samesite="lax"
#         )
#         return response
#
#     print("已访问过")


#     return await call_next(request)

# endregion


# query = select(items).where(and_(items.c.NAME == "寻找无间地狱", items.c.TITLE == "第一章 一个顾客"))
# result = await database.fetch_all(query)
# print(result)
# query = select(items).where((items.c.NAME == "寻找无间地狱") & (items.c.TITLE == "第一章 一个顾客"))
# result = await database.fetch_all(query)
# print(result)
# PROTECTED_PATHS = ["/", "/1" ]
# @app.middleware("http")
# async def auth_middleware(request: Request, call_next ):
#     # 检查请求路径是否需要登录
#     # print('进入中间件输出 ')
#     # print('中间件输出cookie：'+str( request.cookies))
#     # if  request.url.path  in PROTECTED_PATHS:
#     #     return await call_next(request)
#     # if request.cookies is None:
#     #     return RedirectResponse(url="/")
#     response = await call_next(request)
#     return response


# 添加认证中间件（注意顺序要在SessionMiddleware之后）


@app.get("/set-cookie")
def set_cookie(response: Response):
    response.set_cookie(
        key="test_cookie",   # 键
        value="hello_world",  # 值
        httponly=True,  # 允许 JS 访问（仅开发测试用）
        secure=False,    # 允许 HTTP（仅开发测试用）
        samesite="lax",   # 防止 CSRF
        domain=None,     # 允许所有域名访问
        path="/",       #  允许所有路径访问
        max_age=3600,  # 1小时过期
        expires=datetime.datetime.utcnow() + datetime.timedelta(days=1)  # 明确过期时间（秒）
    )
    return {"message": "Cookie set"}


@app.get("/")
async def root(request: Request):
    # response.set_cookie(
    #     key="test_cookie",
    #     value="123435",
    #     httponly=True,
    #     secure=False,  # 开发环境必须为False
    #     max_age=3600,
    #     path="/",
    #     samesite="lax",
    #     domain=None,
    #     # 新增以下参数
    #     expires=3600  # 明确过期时间（秒）
    # )
    # request.session["user"] = "21321"
    # print("ROOT - Cookies being set:", response.headers.get("set-cookie"))
    # session = request.session.get('user')
    # print(session)
    # return HTMLResponse("""
    # <html>
    #     <body>
    #         <h1>首页</h1>
    #         <a href='/1'  >跳转到页面1</a>
    #         <a href='/2'  >清除会话</a>
    #         <a href='/users/index'>返回用户页</a>
    #     </body>
    # </html>
    # """)

    return templates.TemplateResponse("404.html" , {"request": request})

@app.get("/2")
async def root2(request: Request,response: Response,cookies:str= Cookie(None)):
    user={"name":"admin","role":"管理员"}
    response.set_cookie(key="uuuu", value="1234567890",max_age=3600)
    # response.set_cookie(
    #     key="test_cookie",
    #     value="123435",
    #     httponly=False,
    #     secure=False,  # 开发环境必须为False
    #     max_age=3600,
    #     path="/",
    #     samesite="lax",
    #     domain='localhost',
    #     # 新增以下参数
    #     expires=3600  # 明确过期时间（秒）
    # )
    cookies = request.cookies
    print("All cookies:", cookies)
    print(cookies)
    print(type( cookies))
    print(cookies.get('user'))
    return templates.TemplateResponse("404.html" , {"request": request})

@app.get("/1")
async def root1(request: Request):
    # session = request.session
    # print("All cookies:", request.headers.get('set-cookie'))
    # print(session)
    urls = "<a href='/'>跳转到2</a>"
    data = [{"name": "张三", "age": 20, "sex": "男", "phone": "13812345678"},
            {"name": "李四", "age": 25, "sex": "女", "phone": "13812345678"},
            {"name": "王五", "age": 22, "sex": "女", "phone": "13812345678"},
            {"name": "赵六", "age": 23, "sex": "女", "phone": "13812345678"},
            {"url": "<a href='/'>跳转到2</a>"}
            ]
    # return HTMLResponse(f"""
    # <html>
    #     <body>
    #         <h1>页面1</h1>
    #         <p>当前会话: { }</p>
    #         <p>收到的Cookie: {request.cookies.get('set-cookie')}</p>
    #         <a href='/'>返回首页</a>
    #         <a href='/2'  >清除会话</a>
    #         <a href='/users/index'>返回用户页</a>
    #     </body>
    # </html>
    # """)
    return templates.TemplateResponse("404.html" , {"request": request})

#region
# @app.get("/get_html")
# async def get_html(url: str):
#     global htmls, names, snum, txtlist, lists, listError
#     htmls = ''
#     names = ''
#     snum = ''
#     txtlist = []
#     lists = []
#     listError = []
#     print("--------------------------" + url)
#     html_content = requests.get(url)
#     html_content.encoding = "utf-8"
#     htmls = html_content.text
#     return {"data": html_content.text}
#
#
# def convert_chinese_numbers(text):
#     # 匹配所有中文数字（包括单位）
#     pattern = r'[零一二三四五六七八九十百千万亿两]+'
#     matches = re.findall(pattern, text)
#     for match in matches:
#         try:
#             arabic_num = cn2an.cn2an(match, "smart")
#             text = text.replace(match, str(arabic_num))
#         except:
#             continue
#     return ''.join(filter(str.isdigit, text))
#
#
# @app.get("/getname")
# async def getname(strs: str):
#     global htmls
#     tree = html.fromstring(htmls)  # 使用 lxml.html.fromstring 解析 HTML
#     title = tree.xpath(strs)  # 提取 title 标签的内容
#     # //div[@id='info']/h1/text()
#     global names
#     names = title[0]
#     # print(title)
#     return {"name": title}
#
#
# @app.get("/getTU")
# async def getTU(strs: str, ck: int):
#     global htmls
#     # print(strs)
#     # print(htmls)
#     tree = html.fromstring(htmls)  # 使用 lxml.html.fromstring 解析 HTML
#     taga = tree.xpath(strs)  # 提取 title 标签的内容
#     global lists
#     for url in taga:
#         urls = url.xpath("@href")
#         if ck == 1:
#             title = url.xpath("@title")
#         else:
#             title = url.xpath("text()")
#         lists.append([urls[0], title[0]])
#     # print(lists)
#     return {"data": lists}
#
#
# # @app.post("/uploadfile/")
# # async def create_upload_file(file: UploadFile):
# #     print({"filename": file.filename})
# #     with open(file, "wb+") as f:
# #         shutil.copyfileobj(file.file, f)
# #     return {"msg":"上传成功","filename": file.filename}
#
#
# @app.get("/getText")
# async def getText(urls: str, tag: str):
#     try:
#         global names
#         # query = items.delete().where(items.c.NAME == names)
#         # query = items.update().values(TXT=txt).where(items.c.NAME == txt)
#         # await database.execute(query)
#         global htmls, lists
#         tasks = []
#         i = 0
#         for url, title in lists:
#             i = i + 1
#             if i % 200 == 0:
#                 # break
#                 await asyncio.sleep(3)
#             if url.strip() == '':
#                 continue
#             if not urls.strip() == '':
#                 url = urls.strip() + url.split(',')[0]
#             else:
#                 url = url.split(',')[0]
#             if '请假' in title or '休息' in title:
#                 continue
#             tasks.append(asyncio.create_task(get_html_txt(url, title, tag)))
#         await asyncio.gather(*tasks)
#         time = datetime.datetime.now()
#         # await asyncio.sleep(5)
#         global txtlist
#         # print(txtlist[0])
#         # await save_html(txtlist[0])
#         threads = []
#         i = 0
#         for txt in txtlist:
#             i = i + 1
#             if i % 30 == 0:
#                 await asyncio.sleep(5)
#             threads.append(asyncio.create_task(save_html(txt)))
#         await asyncio.gather(*threads)
#         global listError
#         while len(listError) > 0:
#             error = listError
#             listError = []
#             for txt in error:
#                 i = i + 1
#                 if i % 30 == 0:
#                     print(i)
#                     await asyncio.sleep(5)
#                 threads.append(asyncio.create_task(save_html(txt)))
#             await asyncio.gather(*threads)
#             print("*****************************")
#             print("*****************************")
#             print("*****************************")
#             print("*****************************")
#             print("*****************************")
#             print("保存失败信息:")
#             for txt in listError:
#                 print(txt[0])
#             print("*****************************")
#             print("*****************************")
#             print("*****************************")
#             print("*****************************")
#             print("*****************************")
#             # global listError
#         time2 = datetime.datetime.now()
#         # print("保存成功,用时:" + str(time2 - time))
#         return {"msg": "小说保存成功"}
#     except:
#         return {"msg": "获取失败"}
#
#
# # print(urls)
# # await get_html(urls)
# # tree = html.fromstring(htmls)  # 使用 lxml.html.fromstring 解析 HTML
# # taga = tree.xpath(txt)  # 提取 title 标签的内容
# # lists=[ ]
# # for url in taga:
# #     urls=url.xpath("@href")
# #     if ck==1:
# #         title=url.xpath("@title")
# #     else:
# #         title=url.xpath("text()")
# #     lists.append([urls[0],title[0]])
# # print(lists)
#
#
# async def save_html(txt: list):
#     global names, snum
#     if snum == '':
#         snum = 0
#     num = 0
#     # await asyncio.sleep(5)  # 修改这里，使用异步的 sleep
#     try:
#         title = txt[0]
#         content = txt[1]
#         if '（' in title and '）' in title:
#             strs = title.split('（')[1].split('）')[0]
#             if len(strs) > 3:
#                 title = title.split('（')[0]
#         num = 0
#         if re.search("千.十", title):
#             print("匹配成功：" + title)
#             title = title.replace("千", "千零")
#         print("开始保存:" + title)
#         if '章' not in title:
#             num = snum + 1
#         else:
#             num = title.split('章')[0]
#             num = convert_chinese_numbers(num)
#             snum = int(num)
#         time = datetime.datetime.now()
#
#         # query = select(items.c.TITLE, items.c.TXT).where(items.c.NAME == names).order_by(items.c.NUMS)
#         query = select(items.c.ID).where((items.c.NAME == names) & (items.c.TITLE == title))
#         result = await database.fetch_all(query)
#         if len(result) == 0:
#             query = items.insert().values(NAME=names, TITLE=title, TXT=content, NUMS=num)
#             query = insert(items).values(NAME=names, TITLE=title, TXT=content, NUMS=num)
#             time2 = datetime.datetime.now()
#             await database.execute(query)
#             print("保存成功:            " + title)
#         else:
#             query = update(items).where((names == items.c.NAME) & (items.c.TITLE == title)).values(TXT=content)
#             print("已存在:              " + title)
#     except Exception as e:
#         global listError
#         listError.append(txt)
#         print('num:' + num)
#         print("保存失败:" + title + ", 错误信息: {" + str(e) + "}")
#         # return {"data": html_content}
#
#
# # async def Del_title(title: str, content: str):
# #     query = items.delete().where(items.c.TITLE == title)
# #     await database.execute(query)
# #     print("删除成功:" + title)
# #
# # async def upd_title(title: str, content: str):
# #     query = items.update().where(items.c.TITLE == title).values(TXT=content)
# #     await database.execute(query)
# #     print("修改成功:" + title)
#
# async def get_html_txt(url, title, tag):
#     html_content = ""
#     # requests.get不能异步不执行
#     # html_content=requests.get(url)
#     # 替代requests.get且异步执行
#     if '章' not in title:
#         htmls = requests.get(url)
#         htmls.encoding = "utf-8"
#         html_content = htmls.text
#     else:
#         async with aiohttp.ClientSession() as session:
#             async with session.get(url) as response:
#                 html_content = await response.text()
#     tree = html.fromstring(html_content)
#     content = tree.xpath(tag)
#     text = ""
#     for content in content:
#         if content.strip() != '':
#             text += "    " + content.strip() + "\r\n"
#     global txtlist
#     print('获取内容成功' + title)
#     txtlist.append([title, text])
#
#
# @app.get("/downtxt")
# async def get_txt():
#     root = tk.Tk()
#     root.withdraw()  # 隐藏主窗口
#     # 临时创建一个 Toplevel 窗口并置顶
#     temp_root = tk.Toplevel(root)
#     temp_root.attributes('-topmost', True)  # 强制置顶
#     temp_root.withdraw()  # 隐藏临时窗口（仅用于控制对话框）
#
#     # 弹出目录选择对话框（继承 temp_root 的置顶属性）
#     directory = filedialog.askdirectory(parent=temp_root)
#
#     # root = tk.Tk()
#     # root.withdraw()  # 隐藏主窗口
#     # directory = filedialog.askdirectory()  # 弹出目录选择对话框
#     # return directory
#     global names
#     query = select(items.c.TITLE, items.c.TXT).where(names == items.c.NAME).order_by(items.c.NUMS)
#     # query = items.select().with_only_columns([items.c.TITLE, items.c.TXT]).where(items.c.NAME == names).order_by(items.c.NUMS)
#     result = await database.fetch_all(query)
#     if len(result) > 0:
#         # 假设你想保存到当前目录下的 result.txt 文件
#         save_path = os.path.join(directory, names + ".txt")
#         with open(save_path, "w", encoding="utf-8") as file:
#             for row in result:
#                 file.write(f"{row[0]}\r\n")
#                 file.write(f"{row[1]}\r\n")
#                 print(f"保存完成: {row[0]}")
#         print({"message": "文件保存成功", "path": save_path})
#         return {"message": "文件保存成功", "path": save_path}
#     else:
#         return {"message": "没有找到匹配的内容"}
#
#
# @app.get("/hello/{name}")
# async def say_hello(name: str):
#     return {"message": f"Hello {name}"}
#
#
# # 自定义 404 页面
# @app.exception_handler(404)
# async def not_found_handler(request: Request, exc: HTTPException):
#     return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
#
#
# # 自定义 500 页面
# @app.exception_handler(Exception)
# async def server_error_handler(request: Request, exc: Exception):
#     return templates.TemplateResponse("500.html", context={"request": request}, status_code=500)
#
#
# # 触发 404
# @app.get("/nothing")
# async def nothing():
#     raise HTTPException(status_code=404)
#
#
# # 触发 500
# @app.get("/error")
# async def error():
#     raise RuntimeError("Database connection failed!")
#endregion

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=88, reload=True )
    # uvicorn.run("main:app", host="0.0.0.0", port=88, reload=True)
    # uvicorn.run("main:app", host="127.0.0.1", port=88, reload=True, log_level="debug")
    # uvicorn main:app --host localhost --port 88 --reload --log-level trace
    # uvicorn main:app --host 127.0.0.1 --port 88 --reload
    # uvicorn main:app --host 0.0.0.0 --port 88 --reload

