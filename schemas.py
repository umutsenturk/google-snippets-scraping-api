#!/usr/bin/env python3
from pydantic import BaseModel, Field
from typing import Optional


class ScrapingData(BaseModel):

    main_search_line: Optional[str]
    parent_search_line: Optional[str]
    snippet: Optional[str]
    url: Optional[str]

    class Config:
        orm_mode = True


class UsersData(BaseModel):

    username: Optional[str]
    password: Optional[str]

    class Config:
        orm_mode = True


class ScrapeMulti(BaseModel):

    search_string: Optional[str]
    sha: Optional[str]

    class Config:
        orm_mode = True


def ResponseModel(data, message):
    return {
        "data": [data],
        "code": 200,
        "message": message,
    }
