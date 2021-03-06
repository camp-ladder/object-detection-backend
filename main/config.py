from main import *
from flask import Blueprint
from pymongo import MongoClient  # DB


SECRET_KEY = 'ladder'


def get_db():
    client = MongoClient('localhost', 27017)

    return client.ladder


def get_key():
    return SECRET_KEY


########################################################################
########################################################################
########################################################################
# 토근 활성화
########################################################################
########################################################################
########################################################################


def authorize(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not 'Authorization' in request.headers:  # headers 에서 Authorization 인증을 하고
            abort(401)  # Authorization 으로 토큰이 오지 않았다면 에러 401
        # Authorization 이 headers에 있다면 token 값을 꺼내온다.
        token = request.headers['Authorization']
        try:
            user = jwt.decode(token, SECRET_KEY, algorithms=[
                              'HS256'])  # 꺼내온 token 값을 디코딩해서 꺼내주고
        except:
            abort(401)  # 디코딩이 안될 경우 에러 401
        return f(user, *args, **kwargs)
    return decorated_function
