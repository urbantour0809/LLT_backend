from flask import Flask, jsonify, render_template
from flask_cors import CORS
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
import os
import logging

app = Flask(__name__)
CORS(app)  # CORS를 Flask 앱에 적용

# 로그 설정
logging.basicConfig(level=logging.INFO)

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
    start_lotto_round = 1142  # 기준 회차
    start_date = datetime(2024, 10, 19)  # 기준 회차의 날짜
    today = datetime.today()
    delta_days = (today - start_date).days
    delta_weeks = delta_days // 7  # 주 차이 계산
    current_round = start_lotto_round + delta_weeks  # 현재 회차 계산
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

# 로또 번호 예측 API
@app.route('/generate-lotto')
def generate_lotto():
    lotto_numbers = load_lotto_data(os.path.join(os.path.dirname(__file__), 'lotto_numbers.txt'))
    predictions = predict_lotto_numbers(lotto_numbers)
    current_round = get_lotto_round()  # 현재 회차 계산
    return jsonify(numbers=predictions, round=current_round)

# 포트 설정 (Cloudtype에서 자동 할당)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Cloudtype에서 동적으로 포트를 할당
    app.run(host='0.0.0.0', port=port)
