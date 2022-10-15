#!/usr/bin/env python3

import os
import motor.motor_asyncio

MONGO_DETAILS = os.getenv("MONGO_DETAILS")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

db = client.snippets

snippet_collection = db.get_collection("snippets")
users_collection = db.get_collection("dbusers")


def snippet_helper(snippet) -> dict:
    return {
        "id": str(snippet["_id"]),
        "main_search_line": str(snippet["main_search_line"]),
        "parent_search_line": str(snippet["parent_search_line"]),
        "snippet": str(snippet["snippet"]),
        "url": str(snippet["url"]),
    }
