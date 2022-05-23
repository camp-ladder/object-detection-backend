########################################################################
########################################################################
# 회원가입, 로그인
########################################################################
########################################################################

from main import *
from flask import Blueprint

# DB 호출
# from werkzeug.local import LocalProxy
# db = LocalProxy(get_db)

from . import config

db = config.get_db()
SECRET_KEY = config.get_key()


blueprint = Blueprint("member", __name__, url_prefix='')


########################################################################
########################################################################
########################################################################
# 토근 활성화
########################################################################
########################################################################
########################################################################


def authorize(f):
    @wraps(f)
    def decorated_function():
        if not 'Authorization' in request.headers:  # headers 에서 Authorization 인증을 하고
            abort(401)  # Authorization 으로 토큰이 오지 않았다면 에러 401
        # Authorization 이 headers에 있다면 token 값을 꺼내온다.
        token = request.headers['Authorization']
        try:
            user = jwt.decode(token, SECRET_KEY, algorithms=[
                              'HS256'])  # 꺼내온 token 값을 디코딩해서 꺼내주고
        except:
            abort(401)  # 디코딩이 안될 경우 에러 401
        return f(user)
    return decorated_function


########################################################################
########################################################################
########################################################################
# index
########################################################################
########################################################################
########################################################################
@blueprint.route('/')
@authorize  # decorated 함수 적용
def index(user):
    # print(user)
    return jsonify({'message': 'success'})


########################################################################
########################################################################
########################################################################
# 회원가입
########################################################################
########################################################################
########################################################################
@blueprint.route("/signup", methods=["POST"])
def signup():
    data = json.loads(request.data)

    # DB 에 저장할 테이블 명
    user_id_receive = data["user_id"]
    email_receive = data["email"]
    password_receive = data["password"]
    password_check_receive = data["password_check"]
    user_age_receive = data["user_age"]

    # 입력 정보에 대한 에러
    try:
        if not user_id_receive or not email_receive:
            sign_error = 770
            return jsonify({'message': 'fail', 'sign_error': sign_error})
        elif '@' not in email_receive or '.' not in email_receive:
            sign_error = 771
            return jsonify({'message': 'fail', 'sign_error': sign_error})
        elif not password_receive or not password_check_receive:
            sign_error = 772
            return jsonify({'message': 'fail', 'sign_error': sign_error})
        elif password_receive != password_check_receive:
            sign_error = 773
            return jsonify({'message': 'fail', 'sign_error': sign_error})
        elif not user_age_receive:
            sign_error = 774
            return jsonify({'message': 'fail', 'sign_error': sign_error})
            # 중복 처리
        elif db.ladder.find_one({'user_id': user_id_receive}):
            sign_error = 775
            return jsonify({'message': 'fail', 'sign_error': sign_error})
        elif db.ladder.find_one({'email': email_receive}):
            sign_error = 776
            return jsonify({'message': 'fail', 'sign_error': sign_error})
    except:
        status = 200
        return jsonify({'message': 'success', 'status': status})

    password_hash = hashlib.sha256(
        data["password"].encode('utf-8')).hexdigest()

    doc = {
        'user_id': data.get('user_id'),
        'email': data.get('email'),
        'password': password_hash,
        'user_age': data.get('user_age'),
    }

    db.ladder.insert_one(doc)

    return jsonify({'message': 'success'})


########################################################################
########################################################################
########################################################################
# 로그인
########################################################################
########################################################################
########################################################################
@blueprint.route("/login", methods=["POST"])
def login():
    data = json.loads(request.data)
    # print(data)

    user_id = data.get("user_id")
    password = data.get("password")
    hashed_pw = hashlib.sha256(password.encode('utf-8')).hexdigest()  # 복호화
    # print(hashed_pw)

    # 아이디 비밀번호 검사
    result = db.ladder.find_one({
        "user_id": user_id,
        "password": hashed_pw,
    })
    # print(result)

    if result is None:
        return jsonify({'message': 'fail'}), 401

    # 토큰 정의
    payload = {
        'id': str(result['_id']),
        'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 토큰 시간 적용
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    print(token)

    return jsonify({'message': 'success', 'token': token})


########################################################################
########################################################################
########################################################################
# userinfo
########################################################################
########################################################################
########################################################################
@blueprint.route("/getuserinfo", methods=["GET"])
@authorize
def get_user_info(user):
    result = db.ladder.find_one({
        '_id': ObjectId(user['id'])
    })

    print(result)

    return jsonify({'message': 'success', 'email': result['email']})