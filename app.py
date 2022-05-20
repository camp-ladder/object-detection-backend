from audioop import findfactor
from datetime import datetime
from io import BytesIO
import json
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from PIL import Image
import base64
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.deep_pro



app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})


@app.route('/')
# @authrize
def login_page():
    return render_template('index.html')


@app.route('/post', methods=['POST'])
def post_file():
# if user is not None:
    files = request.files.to_dict() # ImmutableMultiDict을 객체로 변환
    for file in files.values():
        current_time = datetime.now() # 현재 시간
        ext = file.filename.split('.')[-1]  # 이미지 확장자 추출
        filename = f"{current_time.strftime('%Y%m%d%H%M%S')}.{ext}" # 이미지 이름 설정

        save_to = f'static/img/upload_img/{filename}'  # 경로지정
        file.save(save_to)  # 이미지 파일 저장

        input_age = request.form['input_age']

        doc = {
            # 'user_id': user_id,
            # 'user_nick_name': user_nick_name,
            'img_name': filename,
            'input_age': input_age,
            # 'timestamp': datetime.utcnow()   
        }
    db.posts.insert_one(doc)
    return jsonify({'msg': '저장완료!', 'filename': filename})


# 파일 정보 보내기
@app.route('/posts', methods=['POST'])
def get_file():
    data = json.loads(request.data)
    filename = data.get("filename")
    post = db.posts.find_one({'img_name': filename})
    post["_id"] = str(post["_id"])
    print(post)
    return jsonify({'msg': '저장완료!', 'post': post})


# @app.route('/posts', methods=['POST'])
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
#         file_list.append(image_base64)
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)