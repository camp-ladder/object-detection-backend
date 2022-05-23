########################################################################
########################################################################
########################################################################
# app 객체 선언, 각종 모듈, 데이터베이스, 블루프린트 설정
########################################################################
########################################################################
########################################################################
from datetime import timedelta
import datetime
from functools import wraps
import hashlib
import json
from unittest import result
from bson import ObjectId
from flask import Flask, abort, jsonify, request, Response, Blueprint
from flask_cors import CORS  # flask 연결
from pymongo import MongoClient  # DB
import jwt
# 이미지 업로드
from PIL import Image
import base64
import os
from io import BytesIO
from audioop import findfactor

# 머신러닝 모델
from mtcnn import MTCNN
import cv2
import numpy as np
import tensorflow as tf
from keras.models import load_model
import time
import math

from . import member  # member 호출
from . import board  # board 호출
from . import age_cal  # model 호출

########################################################################
########################################################################
# 객체 선언
########################################################################
########################################################################


app = Flask(__name__)  # app 객체 선언
# SECRET_KEY = 'ladder'
# app.config["MONGO_URI"] = "mongodb://localhost:27017/WhisperTalk" # pymongo DB 경로 설정
# salt = 'ladder'  # SECRET_KEY
# now = str(datetime.now())
# myHash = hashlib.sha512(str(now + salt).encode('utf-8')).hexdigest()
# app.config['SECRET_KET'] = myHash
# mongo = pymongo(app)
cors = CORS(app, resources={r"*": {"origins": "*"}})

# pymongo DB 경로 설정
# app.config["MONGO_URI"] = "mongodb://localhost:27017/ladder"
client = MongoClient('localhost', 27017)
db = client.ladder


# def get_db():
#     db = getattr(g, '_database', None)
#     if db is None:
#         db = g._database = connect_to_database()
#     return db

# @app.teardown_appcontext
# def teardown_db(exception):
#     db = getattr(g, '_database', None)
#     if db is not None:
#         db.close()


########################################################################
########################################################################
# url 연결
########################################################################
########################################################################

app.register_blueprint(member.blueprint)
app.register_blueprint(board.blueprint)
app.register_blueprint(age_cal.age_cal)
