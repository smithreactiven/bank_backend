import asyncio
import logging
import os
import re
import typing
import requests
import config
from flask import Flask, jsonify, request, Response
from aiogram import Bot, types
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import validator
import redis
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from datetime import datetime
import tools
import database
from sqlalchemy import select
import models
from redis.commands.json.path import Path
import aiofiles
from get_filepaths import get_filepaths_with_oswalk
import boto3

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app = Flask(__name__, static_folder="static", static_url_path='/api/static/')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = database.implement.PostgreSQL(
    database_name=config.POSTGRESQL_DBNAME,
    username=config.POSTGRESQL_USER,
    password=config.POSTGRESQL_PASSWORD,
    hostname=config.POSTGRESQL_HOST,
    port=config.POSTGRESQL_PORT
)

session = database.manager.create_session(db)


@app.post("/api/checkInitData")
async def check_init_data():
    data = request.json
    data = validator.safe_parse_webapp_init_data(config.BOT_TOKEN, data["_auth"])
    print(data)

    return data.model_dump_json()


@app.post("/api/topUpBalance")
async def top_up_balance():
    replenishment = request.json["replenishment"]
    user_id = request.json["user_id"]
    print(user_id)
    with session() as open_session:
        user = open_session.execute(select(models.sql.User).filter_by(id=user_id))
        user = user.scalars().first()
        new_check = int(user.check) + int(replenishment)
        user.check = new_check
        open_session.commit()
    return jsonify(dict(balance=new_check))


@app.post("/api/viewBalance")
async def check_balance():
    user_id = request.json["user_id"]
    with session() as open_session:
        user = open_session.execute(select(models.sql.User).filter_by(id=user_id))
        user = user.scalars().first()
        balance = int(user.check)

    return jsonify(dict(balance=balance))


if __name__ == "__main__":
    app.run("localhost", port=5001)






