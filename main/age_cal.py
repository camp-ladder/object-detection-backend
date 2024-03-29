from main import *
from flask import Blueprint as age_cal

from . import config

db = config.get_db()
SECRET_KEY = config.get_key()

age_cal = Blueprint("age_cal", __name__,
                    static_folder='static', template_folder='templates')

sex_model = load_model('main/model/all_face_sex_model.h5')
male_age_model = load_model('main/model/all_face_male_age_model.h5')
female_age_model = load_model('main/model/all_face_female_age_model.h5')

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
        age_pred = float(age_pred)
    else:
        sex = '남자'
        age_pred = male_age_model.predict(input_arr)
        age_pred = float(age_pred)
    
    return sex, age_pred


def age_cal_model(user, filename, extension, save_to):
    img = cv2.imread('main/' + save_to)
    detector = MTCNN()
    detections = detector.detect_faces(img)
    if len(detections) == 0:
        person = 0
        doc = {}
        os.remove('main/' + save_to)
        return person, doc
    elif len(detections) >= 2:
        person = 2
        doc = {}
        os.remove('main/' + save_to)
        return person, doc

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
            cv2.imwrite(
                f'main/static/img/result/{filename}_{str(imgNum)}.{extension}', cropped)
            imgNum += 1
    ages_dict = {}
    for i in range(imgNum):
        exam_img = f'static/img/result/{filename}_{str(i)}.{extension}'
        sex, age_pred = process_and_predict('main/' + exam_img)
        age_pred = round(age_pred)
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
        person = 1
    return person, doc


@age_cal.route('/calculator', methods=['POST'])
@config.authorize
def calculator(user):
    files = request.files.to_dict()  # ImmutableMultiDict을 객체로 변환
    for file in files.values():
        current_time = datetime.datetime.now()
        extension = file.filename.split('.')[-1]  # 이미지 확장자 추출
        filename = f"{current_time.strftime('%Y%m%d%H%M%S')}"

        save_to = f'static/img/original/{filename}.{extension}'
        file.save('main/' + save_to)

    input_age = request.form['input_age']

    time.sleep(1)

    person, result = age_cal_model(user, filename, extension, save_to)
    result['input_age'] = input_age
    return jsonify({'person': person, 'result': result})