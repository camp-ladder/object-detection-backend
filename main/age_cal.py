from main import *
from flask import Blueprint as age_cal

# DB 호출
# from werkzeug.local import LocalProxy
# db = LocalProxy(get_db)

from . import config

db = config.get_db()
SECRET_KEY = config.get_key()

# blueprint = Blueprint("member", __name__, url_prefix='')

age_cal = Blueprint("age_cal", __name__,
                    static_folder='static', template_folder='templates')


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


sex_model = load_model('main/model/all_face_sex_model.h5')
male_age_model = load_model('main/model/all_face_male_age_model.h5')
female_age_model = load_model('main/model/all_face_female_age_model.h5')
# asian_age_model = load_model('asian_age_model.h5')
# all_age_model = load_model('all_face_model.h5')


def process_and_predict(file):
    image = tf.keras.preprocessing.image.load_img(file, target_size=(200, 200))
    input_arr = tf.keras.preprocessing.image.img_to_array(image)
    input_arr = np.array([input_arr])
    input_arr = input_arr.astype('float32')
    input_arr /= 255.0
    input_arr = input_arr.reshape(-1, 200, 200, 3)

    sex_pred = sex_model.predict(input_arr)
    if sex_pred[0][0] > 0.5:
        sex = '여자'
        age_pred = female_age_model.predict(input_arr)
        # age_pred = asian_age_model.predict(input_arr)
    #   age_pred = all_age_model.predict(input_arr)
        age_pred = float(age_pred)
    else:
        sex = '남자'
        age_pred = male_age_model.predict(input_arr)
        # age_pred = asian_age_model.predict(input_arr)
    #   age_pred = all_age_model.predict(input_arr)
        age_pred = float(age_pred)

    return sex, age_pred


def age_cal_model(user, img_file, filename, extension, save_to):
    img = cv2.imread('main/' + img_file)
    detector = MTCNN()
    detections = detector.detect_faces(img)

    min_conf = 0.9
    imgNum = 0
    for det in detections:
        if det['confidence'] >= min_conf:
            x, y, w, h = det['box']
            if w >= h:
                cropped = img[int(
                    (2*y + h - w)/2 - w/4): int((2*y + h + w)/2 + w/4), int(x - w/4): int(x + w + w/4)]
            else:
                cropped = img[int(y - h/4): int(y + h + h/4),
                              int((2*x + w - h)/2 - h/4): int((2*x + w + h)/2 + h/4)]
        # 이미지를 저장
            cv2.imwrite(
                f'main/static/img/result/{filename}_{str(imgNum)}.{extension}', cropped)
            imgNum += 1
    ages_dict = {}
    for i in range(imgNum):
        exam_img = f'static/img/result/{filename}_{str(i)}.{extension}'
        sex, age_pred = process_and_predict('main/' + exam_img)
        age_pred = round(age_pred)  # 소수점 반올림
        ages_dict[exam_img] = [sex, age_pred]
        doc = {
            'user_id': user['id'],
            'post_id': '',
            'original_title': save_to,
            'result_title': exam_img,
            'sex': sex,
            'age_pred': age_pred
        }
        db.results.insert_one(doc)

        doc["_id"] = str(doc["_id"])

    return doc


@age_cal.route('/calculator', methods=['POST'])
@config.authorize
def calculator(user):
    # file_receive = request.files['file_give']
    # extension = file_receive.filename.split('.')[-1]

    # now = datetime.datetime.now()
    # time_now = now.strftime('%Y-%m-%d-%H-%M-%S')
    # filename = f'img_{time_now}'
    # save_to = f'main/static/img/original/{filename}.{extension}'
    # file_receive.save(save_to)
    files = request.files.to_dict()  # ImmutableMultiDict을 객체로 변환
    for file in files.values():
        current_time = datetime.datetime.now()  # 현재 시간
        extension = file.filename.split('.')[-1]  # 이미지 확장자 추출
        filename = f"{current_time.strftime('%Y%m%d%H%M%S')}"

        print(user)
        save_to = f'static/img/result/{filename}.{extension}'  # 경로지정
        file.save('main/' + save_to)  # 이미지 파일 저장

    print(filename)

    # # MongoDB 저장 만들어야함
    # doc = {
    #     'img_title': save_to
    # }
    # db.originals.insert_one(doc)

    time.sleep(1)

    result = age_cal_model(user, save_to, filename, extension, save_to)
    return jsonify({'result': result})
