from flask import Flask, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import os
from dotenv import load_dotenv
from auth import auth  # auth 블루프린트 임포트

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# CORS 설정 (프론트엔드 도메인 명시)
CORS(app, supports_credentials=True, origins=['https://llt-aws.vercel.app'])
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.register_blueprint(auth)  # 블루프린트 등록

# 사용자 모델 정의
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(50))
    age = db.Column(db.Integer)
    gender = db.Column(db.Enum('M', 'F'))

# 초기화 시 데이터베이스 생성
with app.app_context():
    db.create_all()

# 모델 로드
model = load_model(os.path.join(os.path.dirname(__file__), 'lotto_model.h5'))

# 로또 데이터 txt 파일에서 데이터 로드
def load_lotto_data(file_name):
    with open(file_name, 'r') as file:
        lines = file.readlines()
    lotto_numbers = [list(map(int, line.strip().split(','))) for line in lines]
    return lotto_numbers

# 회차 계산 함수
def get_lotto_round():
    start_lotto_round = 1143
    start_date = datetime(2024, 10, 20)
    today = datetime.today()
    delta_days = (today - start_date).days
    delta_weeks = delta_days // 7
    current_round = start_lotto_round + delta_weeks
    return current_round

# 데이터 스케일링 함수
def scale_data(lotto_numbers):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(lotto_numbers)
    return scaled_data, scaler

# 중복을 제거하고 부족한 숫자를 채워주는 함수
def remove_duplicates_and_fill(predicted_numbers):
    unique_numbers = list(set(predicted_numbers))
    while len(unique_numbers) < 6:
        new_number = np.random.randint(1, 46)
        if new_number not in unique_numbers:
            unique_numbers.append(new_number)
    return sorted(unique_numbers)

# 번호 예측 함수
def predict_lotto_numbers(lotto_numbers):
    scaled_data, scaler = scale_data(lotto_numbers)
    last_60_days = scaled_data[-60:]
    x_test = np.array([last_60_days])

    predicted_games = []
    for game in range(5):
        predicted_numbers = model.predict(x_test)
        predicted_numbers = scaler.inverse_transform(predicted_numbers)
        predicted_numbers = np.clip(np.around(predicted_numbers).astype(int), 1, 45)
        unique_sorted_numbers = remove_duplicates_and_fill(predicted_numbers[0].tolist())
        predicted_games.append(unique_sorted_numbers)
        new_input = np.concatenate((x_test[:, 1:, :], predicted_numbers.reshape(1, 1, -1)), axis=1)
        x_test = new_input

    return predicted_games

# 로또 번호 예측 API (로그인 필요)
@app.route('/generate-lotto')
def generate_lotto():
    if 'user_id' not in session:
        return jsonify({'error': 'Please log in to generate lotto numbers'}), 403

    lotto_numbers = load_lotto_data(os.path.join(os.path.dirname(__file__), 'lotto_numbers.txt'))
    predictions = predict_lotto_numbers(lotto_numbers)
    current_round = get_lotto_round()
    return jsonify(numbers=predictions, round=current_round)

# 포트 설정 (Cloudtype에서 자동 할당)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
