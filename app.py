import asyncio
import datetime
import os
import re
import os
import aiohttp
import cn2an
import requests
import sqlalchemy
import uvicorn
import tkinter as tk
from databases import Database
from fastapi import HTTPException, Request, FastAPI
from lxml import html
from pydantic import BaseModel
from select import select
from sqlalchemy import insert, Column, Integer, String
from tkinter import filedialog
from turtle import update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from Config import Conn
from blueprints.User import user
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from tortoise.contrib.fastapi import register_tortoise

from models import TXT


class TxtItem(BaseModel):
    id: int
    name: str
    title: str
    txt: str
    nums: int


app = FastAPI()  # , docs_url=None, redoc_url=None, openapi_url=None)

os.makedirs("./static", exist_ok=True)
os.makedirs("./templates", exist_ok=True)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(user, prefix="/users", tags=["users"])

register_tortoise(
    app=app,
    config=Conn,
    # generate_schemas=True,  # 如果数据库为空，则自动生成对应表单，生产环境不要开
    # add_exception_handlers=True,  # 生产环境不要开，会泄露调试信息
)


@app.get("/")
async def home(request: Request):
    #     print("-" * 50)
    #     print(TXT._meta.fields_map.keys())
    #     # await TXT.create(name="123", title="123", txt="123", nums=123)
    #     result =await TXT.filter(txt = "32115")
    #     print(result)
    return templates.TemplateResponse("1.html", {"request": request})


# region
@app.get("/get_html")
async def get_html(url: str):
    global htmls, names, snum, txtlist, lists, listError
    htmls = ''
    names = ''
    snum = ''
    txtlist = []
    lists = []
    listError = []
    print("--------------------------" + url)
    html_content = requests.get(url)
    html_content.encoding = "utf-8"
    htmls = html_content.text
    return {"data": html_content.text}


def convert_chinese_numbers(text):
    # 匹配所有中文数字（包括单位）
    pattern = r'[零一二三四五六七八九十百千万亿两]+'
    matches = re.findall(pattern, text)
    for match in matches:
        try:
            arabic_num = cn2an.cn2an(match, "smart")
            text = text.replace(match, str(arabic_num))
        except:
            continue
    return ''.join(filter(str.isdigit, text))


@app.get("/getname")
async def getname(strs: str):
    global htmls
    tree = html.fromstring(htmls)  # 使用 lxml.html.fromstring 解析 HTML
    title = tree.xpath(strs)  # 提取 title 标签的内容
    # //div[@id='info']/h1/text()
    global names
    names = title[0]
    # print(title)
    return {"name": title}


@app.get("/getTU")
async def getTU(strs: str, ck: int):
    global htmls
    # print(strs)
    # print(htmls)
    tree = html.fromstring(htmls)  # 使用 lxml.html.fromstring 解析 HTML
    taga = tree.xpath(strs)  # 提取 title 标签的内容
    global lists
    for url in taga:
        urls = url.xpath("@href")
        if ck == 1:
            title = url.xpath("@title")
        else:
            title = url.xpath("text()")
        lists.append([urls[0], title[0]])
    # print(lists)
    return {"data": lists}


# @app.post("/uploadfile/")
# async def create_upload_file(file: UploadFile):
#     print({"filename": file.filename})
#     with open(file, "wb+") as f:
#         shutil.copyfileobj(file.file, f)
#     return {"msg":"上传成功","filename": file.filename}


@app.get("/getText")
async def getText(urls: str, tag: str):
    try:
        global names
        # query = items.delete().where(items.c.NAME == names)
        # query = items.update().values(TXT=txt).where(items.c.NAME == txt)
        # await database.execute(query)
        global htmls, lists
        tasks = []
        i = 0
        for url, title in lists:
            i = i + 1
            # if i > 5:
            #     break
            if i % 200 == 0:
                # break
                await asyncio.sleep(3)
            if url.strip() == '':
                continue
            if not urls.strip() == '':
                url = urls.strip() + url.split(',')[0]
            else:
                url = url.split(',')[0]
            if '请假' in title or '休息' in title:
                continue
            tasks.append(asyncio.create_task(get_html_txt(url, title, tag)))
        await asyncio.gather(*tasks)
        time = datetime.datetime.now()
        # await asyncio.sleep(5)
        global txtlist
        # print(txtlist[0])
        # await save_html(txtlist[0])
        threads = []
        i = 0
        for txt in txtlist:
            i = i + 1
            if i % 30 == 0:
                await asyncio.sleep(5)
            # await save_html(txt)
            threads.append(asyncio.create_task(save_html(txt)))
        await asyncio.gather(*threads)
        global listError
        while len(listError) > 0:
            error = listError
            listError = []
            for txt in error:
                i = i + 1
                if i % 30 == 0:
                    print(i)
                    await asyncio.sleep(5)
                threads.append(asyncio.create_task(save_html(txt)))
            await asyncio.gather(*threads)
            print("保存失败信息:")
            for txt in listError:
                print(txt[0])
            # global listError
        time2 = datetime.datetime.now()
        # print("保存成功,用时:" + str(time2 - time))
        return {"msg": "小说保存成功"}
    except:
        return {"msg": "获取失败"}


# print(urls)
# await get_html(urls)
# tree = html.fromstring(htmls)  # 使用 lxml.html.fromstring 解析 HTML
# taga = tree.xpath(txt)  # 提取 title 标签的内容
# lists=[ ]
# for url in taga:
#     urls=url.xpath("@href")
#     if ck==1:
#         title=url.xpath("@title")
#     else:
#         title=url.xpath("text()")
#     lists.append([urls[0],title[0]])
# print(lists)


async def save_html(txt: list):
    global names, snum
    if snum == '':
        snum = 0
    num = 0
    # await asyncio.sleep(5)  # 修改这里，使用异步的 sleep
    try:
        title = txt[0]
        content = txt[1]
        if '（' in title and '）' in title:
            strs = title.split('（')[1].split('）')[0]
            if len(strs) > 3:
                title = title.split('（')[0]
        num = 0
        if re.search("千.十", title):
            print("匹配成功：" + title)
            title = title.replace("千", "千零")
        print("开始保存:" + title)
        if '章' not in title:
            num = snum + 1
        else:
            num = title.split('章')[0]
            num = convert_chinese_numbers(num)
            snum = int(num)
        time = datetime.datetime.now()
        result = await TXT.filter(name=names, title=title)
        if len(result) == 0:
            await TXT.create(name=names, title=title, txt=content, nums=num)
            print("保存成功:            " + title)
        else:
            result[0].nums = num
            result[0].txt = content
            await result[0].save()
            # query = update(items).where((names == items.c.NAME) & (items.c.TITLE == title)).values(TXT=content)
            print("已存在:              " + title)
    except Exception as e:
        global listError
        listError.append(txt)
        print('num:' + num)
        print("保存失败:" + title + ", 错误信息: {" + str(e) + "}")
        # return {"data": html_content}


# async def Del_title(title: str, content: str):
#     query = items.delete().where(items.c.TITLE == title)
#     await database.execute(query)
#     print("删除成功:" + title)
#
# async def upd_title(title: str, content: str):
#     query = items.update().where(items.c.TITLE == title).values(TXT=content)
#     await database.execute(query)
#     print("修改成功:" + title)

async def get_html_txt(url, title, tag):
    html_content = ""
    # requests.get不能异步不执行
    # html_content=requests.get(url)
    # 替代requests.get且异步执行
    if '章' not in title:
        htmls = requests.get(url)
        htmls.encoding = "utf-8"
        html_content = htmls.text
    else:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html_content = await response.text()
    tree = html.fromstring(html_content)
    content = tree.xpath(tag)
    text = ""
    for content in content:
        if content.strip() != '':
            text += "    " + content.strip() + "\r\n"
    global txtlist
    print('获取内容成功' + title)
    txtlist.append([title, text])


@app.get("/downtxt")
async def get_txt():
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    # 临时创建一个 Toplevel 窗口并置顶
    temp_root = tk.Toplevel(root)
    temp_root.attributes('-topmost', True)  # 强制置顶
    temp_root.withdraw()  # 隐藏临时窗口（仅用于控制对话框）

    # 弹出目录选择对话框（继承 temp_root 的置顶属性）
    directory = filedialog.askdirectory(parent=temp_root)

    # root = tk.Tk()
    # root.withdraw()  # 隐藏主窗口
    # directory = filedialog.askdirectory()  # 弹出目录选择对话框
    # return directory
    global names
    result = await TXT.filter(book_name=names).order_by('nums')
    # query = select()
    # # query = items.select().with_only_columns([items.c.TITLE, items.c.TXT]).where(items.c.NAME == names).order_by(items.c.NUMS)
    # result = await database.fetch_all(query)
    if len(result) > 0:
        # 假设你想保存到当前目录下的 result.txt 文件
        save_path = os.path.join(directory, names + ".txt")
        with open(save_path, "w", encoding="utf-8") as file:
            for row in result:
                file.write(f"{row[0]}\r\n")
                file.write(f"{row[1]}\r\n")
                print(f"保存完成: {row[0]}")
        print({"message": "文件保存成功", "path": save_path})
        return {"message": "文件保存成功", "path": save_path}
    else:
        return {"message": "没有找到匹配的内容"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


# 自定义 404 页面
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)


# 自定义 500 页面
@app.exception_handler(Exception)
async def server_error_handler(request: Request, exc: Exception):
    return templates.TemplateResponse("500.html", context={"request": request}, status_code=500)


# 触发 404
@app.get("/nothing")
async def nothing():
    raise HTTPException(status_code=404)


# 触发 500
@app.get("/error")
async def error():
    raise RuntimeError("Database connection failed!")


# endregion


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=88, reload=True)
