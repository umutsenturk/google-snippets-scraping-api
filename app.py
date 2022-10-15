#!/usr/bin/env python3
import hashlib
import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from database import snippet_collection, snippet_helper, users_collection
from bson.objectid import ObjectId
import schemas
import scrape
from fastapi.encoders import jsonable_encoder
from starlette.responses import RedirectResponse, Response
from typing import Any, Dict, AnyStr, List, Union, Optional
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
import requests
from requests.auth import HTTPBasicAuth
import base64
import html
import time
import json
import os

WP_USERNAME = os.getenv("WP_USERNAME")
WP_PASSWORD = os.getenv("WP_PASSWORD")
WP_CATEGORIES_URL = os.getenv("WP_CATEGORIES_URL")
WP_POST_URL = os.getenv("WP_POST_URL")


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.post("/login-verify")
async def login_verify(user_details: schemas.UsersData):
    user = await users_collection.find_one({"username": user_details.username})
    if user:
        if user["password"] == hashlib.sha256(user_details.password.encode()).hexdigest():
            return {"sha256": user["password"]}
        else:
            return {"error": "auth error"}
    else:
        return {"error": "auth error"}


@app.get("/get-all", response_model=List[schemas.ScrapingData])
async def get_all():
    snippets = await retrieve_snippets()
    return jsonable_encoder(snippets)


@app.get("/get-one/{id}", response_model=List[schemas.ScrapingData])
async def get_one_by_id(id: str):
    snippet = await retrieve_snippet(id)
    if not snippet:
        return {"message": "not found"}
    else:
        inner_snippet = await retrieve_inner_snippet(snippet[0]["main_search_line"])
        if inner_snippet:
            for inn in inner_snippet:
                snippet.append(inn)
    return jsonable_encoder(snippet)


@app.post("/post", response_model=schemas.ScrapingData)
async def post_snippet(snippet: schemas.ScrapingData):
    added_snippet = await add_snippet(jsonable_encoder(snippet))
    return jsonable_encoder(added_snippet)


@app.post("/send-data")
async def post_snippets(search_string: str):
    return search_string


@app.post("/scrape-one", response_model=List[schemas.ScrapingData])
async def scrape_one(line: str):
    is_exist_main = await retrieve_snippet(line)
    is_exist_inner = await retrieve_inner_snippet(line)
    if is_exist_main or is_exist_inner:
        is_exist_inner[:0] = is_exist_main
        return jsonable_encoder(is_exist_inner)
    else:
        results = await scrape.get_results(line)
        for res in results:
            await add_snippet(jsonable_encoder(res))
        return jsonable_encoder(results)


@app.post("/scrape-array")
async def scrape_with_array(*, data: schemas.ScrapeMulti):
    user = await retrieve_user_by_sha(data.sha)
    if not user:
        return {"error": "auth error"}

    scraped_data = []
    array = data.search_string.strip("\n").strip(" ").split("\n")
    for line in array:
        data_array = await scrape_one(line)
        for data in data_array:
            scraped_data.append(data)
    return jsonable_encoder(scraped_data)


@app.post("/upload-file")
async def upload_file(*, file: bytes = File(), sha: str):
    user = await retrieve_user_by_sha(sha)
    if not user:
        return {"error": "auth error"}
    scraped_data = []
    for line in file.decode("utf-8").split("\n"):
        data_array = await scrape_one(line)
        for data in data_array:
            scraped_data.append(data)
    return jsonable_encoder(scraped_data)


@app.post("/upload-multiple-file")
async def upload_multiple_files(*, files: List[bytes] = File(), sha: str):
    user = await retrieve_user_by_sha(sha)
    if not user:
        return {"error": "auth error"}
    scraped_data = []

    for file in files:
        for line in file.decode("utf-8").split("\n"):
            data_array = await scrape_one(line)
            for data in data_array:
                scraped_data.append(data)
    return jsonable_encoder(scraped_data)


@app.post("/send-to-wordpress")
async def make_wordpress(*, js: List[schemas.ScrapingData], batchCount: Optional[int] = 30, sha: str, category: Optional[str] = ""):
    user = await retrieve_user_by_sha(sha)
    if not user:
        return {"error": "auth error"}
    try:
        error_titles = []
        empty_array = []
        for i, item in enumerate(js):
            if empty_array == []:
                title = item.main_search_line.title()

            empty_array.append(item)
            if i % batchCount == batchCount - 1 or i == len(js) - 1:
                main_html, urls = await retrieve_wordpress(empty_array)
                combined_str = main_html + urls
                status = await post_to_wordpress(combined_str, title, category)
                if status == 0:
                    error_titles.append(title)
                empty_array = []
        if empty_array == []:
            return {"status": "success"}
        else:
            return {"status": "error on some files: "+str(error_titles)}
    except Exception as e:
        return {"status": "error on some files: "+str(e)+str(error_titles)}


async def post_to_wordpress(body, title, category):

    post_cat = ""
    try:
        try:
            if category != "":
                r_get = requests.get(WP_CATEGORIES_URL,
                                     auth=HTTPBasicAuth(WP_USERNAME, WP_PASSWORD))
                cats = r_get.json()
                for cat in cats:
                    if cat["slug"] == category:
                        post_cat = cat["id"]
        except:
            return 0

        if post_cat != "":
            js = {"title": title, "content": body, "categories": [post_cat]}
        else:
            js = {"title": title, "content": body}

        r_post = requests.post(WP_POST_URL,
                               json=js, auth=HTTPBasicAuth(WP_USERNAME, WP_PASSWORD))

        return 1
    except Exception as e:
        return 0


# Make wordpress content

async def retrieve_wordpress(js):
    main_html = ""
    urls = "<br /><br /><br /><h3>Resources</h3>"
    for i, item in enumerate(js):

        if i != 0:
            main_html += "<h2>" + item.main_search_line.title() + "</h2>"
        main_html += "<p>" + item.snippet + f"[{i+1}]" + "</p>"
        urls += f'<span>[{i+1}]</span><a href="' + \
            item.url + '">' + item.url + "</a><br />"
    return main_html, urls


# DB FUNCTIONS

async def retrieve_snippets():
    snippets = []
    async for snippet in snippet_collection.find():
        snippets.append(snippet_helper(snippet))
    return snippets


async def add_snippet(snippet_data: dict) -> dict:
    snippet = await snippet_collection.insert_one(snippet_data)
    new_snippet = await snippet_collection.find_one({"_id": snippet.inserted_id})
    return snippet_helper(new_snippet)


async def retrieve_user_by_sha(sha: str):

    snippet = await users_collection.find_one({"password": sha})
    if snippet:
        return True
    else:
        return False


async def retrieve_snippet(main_search_line: str) -> dict:
    return_array = []
    # /^bar$/i
    snippet = await snippet_collection.find_one({"main_search_line": main_search_line})
    if snippet:
        return_array.append(snippet_helper(snippet))
    return return_array


async def retrieve_inner_snippet(parent_search_line: str) -> dict:
    inner_snippets = []
    async for snippet in snippet_collection.find({"parent_search_line": parent_search_line}, ):
        inner_snippets.append(snippet_helper(snippet))
    return inner_snippets


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=True)
