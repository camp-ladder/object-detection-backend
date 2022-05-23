########################################################################
########################################################################
# 게시판의 내용 읽기, 쓰기, 목록 확인, 수정, 삭제 등
########################################################################
########################################################################

from main import *
from flask import Blueprint

# DB 호출
from . import config


db = config.get_db()
SECRET_KEY = config.get_key()

blueprint = Blueprint("board", __name__, url_prefix='')


# def authorize(f):
#     @wraps(f)
#     def decorated_function():
#         if not 'Authorization' in request.headers:  # headers 에서 Authorization 인증을 하고
#             abort(401)  # Authorization 으로 토큰이 오지 않았다면 에러 401
#         # Authorization 이 headers에 있다면 token 값을 꺼내온다.
#         token = request.headers['Authorization']
#         try:
#             user = jwt.decode(token, SECRET_KEY, algorithms=[
#                               'HS256'])  # 꺼내온 token 값을 디코딩해서 꺼내주고
#         except:
#             abort(401)  # 디코딩이 안될 경우 에러 401
#         return f(user)
#     return decorated_function


# @blueprint.route('/')
# # @authrize
# def login_page():
#     return render_template('index.html')

# 측정(임시) 하기, 결과 데이터 저장하기


# @blueprint.route('/calculate', methods=['POST'])
# @authorize
# def calculator_temporary(user):
#     files = request.files.to_dict()  # ImmutableMultiDict을 객체로 변환
#     for file in files.values():
#         current_time = datetime.now()  # 현재 시간
#         ext = file.filename.split('.')[-1]  # 이미지 확장자 추출
#         filename = f"{current_time.strftime('%Y%m%d%H%M%S')}.{ext}"

#         print(user)
#         save_to = f'main/static/img/result/{filename}'  # 경로지정
#         file.save(save_to)  # 이미지 파일 저장

#         input_age = int(request.form['input_age'])

#         result = {
#             'user_id': user['id'],
#             # 'user_nick_name': user_nick_name,
#             'post_id': '',
#             'result_img_name': filename,
#             'input_age': input_age,
#             'result_age': 10
#             # 'timestamp': datetime.utcnow()
#         }
#         db.results.insert_one(result)
#         result["_id"] = str(result["_id"])
#         return jsonify({'msg': '저장되었습니다.', "result": result})


# # 결과 데이터 보내기(사용 안 함)
# @blueprint.route('/result/<filename>', methods=['GET'])
# def get_result(filename):
#     result = db.results.find_one({"img_name": filename})
#     print(result)
#     if result:
#         result["_id"] = str(result["_id"])
#         return jsonify({"message": "success", "result": result})
#     else:
#         return jsonify({"message": "fail"}), 404


# 결과 데이터 삭제하기
@blueprint.route('/result/<result_id>', methods=['DELETE'])
@config.authorize
def delete_result(user, result_id):
    result = db.results.find_one(
        {"_id": ObjectId(result_id), "user_id": user['id']})
    result_img_name = result['result_title']
    os.remove(f'main/{result_img_name}')  # result 이미지 삭제

    original_img_name = result['original_title']
    os.remove(f'main/{original_img_name}')  # original 이미지 삭제

    result_del = db.results.delete_one(
        {"_id": ObjectId(result_id)})  # 저장된 결과 데이터 삭제

    if result_del.deleted_count:
        return jsonify({"message": "success"})
    else:
        return jsonify({"message": "fail"}), 403


# 게시물 저장하기
@blueprint.route('/post', methods=['POST'])
@config.authorize
def post_file(user):
    # # if user is not None:
    # files = request.files.to_dict()  # ImmutableMultiDict을 객체로 변환
    # for file in files.values():
    #     current_time = datetime.datetime.now()  # 현재 시간
    #     ext = file.filename.split('.')[-1]  # 이미지 확장자 추출
    #     # 이미지 이름 설정
    #     filename = f"{current_time.strftime('%Y%m%d%H%M%S')}.{ext}"

    #     save_to = f'main/static/img/original/{filename}'  # 경로지정
    #     file.save(save_to)  # 이미지 파일 저장

    result_id = request.form['result_id']
    result = db.results.find_one({"_id": ObjectId(result_id)})

    original_id = result['original_title']

    doc = {
        'user_id': user['id'],
        # 'user_nick_name': user_nick_name,
        'result_id': result_id,
        'img_name': original_id,
        # 'input_age': input_age,
        # 'timestamp': datetime.utcnow()
    }
    db.originals.insert_one(doc)  # posts DB에 저장

    post = db.originals.find_one(
        {"result_id": result_id})  # posts DB의 ObjectId 찾기
    post_id = str(post["_id"])

    db.results.update_one({"_id": ObjectId(result_id)}, {  # result DB에 post_id 저장
        "$set": {"post_id": post_id}
    })

    return jsonify({'msg': '저장되었습니다.'})


# @blueprint.route('/posts', methods=['POST'])
# def post_file():
# # if user is not None:
#     files = request.files.to_dict() # ImmutableMultiDict을 객체로 변환
#     file_list = []
#     for file in files.values():
#         extension = file.filename.split('.')[-1]
#         format = 'JPEG' if extension.lower() == 'jpg' else extension.upper()
#         img = Image.open(file)
#         wpercent = (614/ float(img.size[0]))
#         h_size = int((float(img.size[1]) * float(wpercent)))
#         img_resize = img.resize((614, h_size))
#         buffered = BytesIO()
#         img_resize.save(buffered, format)
#         image_base64 = base64.b64encode(buffered.getvalue())
#         file_list.blueprintend(image_base64)
#     # user_id = user.get('id')
#     # user_nick_name = user.get('nick_name')
#     # content = request.form['content']
#     doc = {
#         # 'user_id': user_id,
#         # 'user_nick_name': user_nick_name,
#         'file' : file_list,
#         # 'content': content,
#         # 'timestamp': datetime.utcnow()
#     }
#     db.posts.insert_one(doc)
#     return jsonify({'msg': '저장완료!'})
