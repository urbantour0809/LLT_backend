from flask import Flask, jsonify, request
from flask_cors import CORS  # CORS 추가
import numpy as np
import pandas as pd
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
try:
    model_path = os.path.join(os.path.dirname(__file__), 'lotto_model.h5')
    model = load_model(model_path)
    logging.info(f"Model loaded successfully from {model_path}")
except Exception as e:
    logging.error(f"Error loading model: {e}")

# 로또 데이터 txt 파일에서 데이터 로드
def load_lotto_data(file_name):
    try:
        with open(file_name, 'r') as file:
            lines = file.readlines()
        lotto_numbers = [list(map(int, line.strip().split(','))) for line in lines]
        logging.info(f"Lotto numbers loaded successfully from {file_name}")
        return lotto_numbers
    except Exception as e:
        logging.error(f"Error loading lotto numbers from {file_name}: {e}")
        return []

# 데이터 스케일링 함수
def scale_data(lotto_numbers):
    try:
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(lotto_numbers)
        logging.info("Lotto data scaled successfully")
        return scaled_data, scaler
    except Exception as e:
        logging.error(f"Error scaling data: {e}")
        return None, None

# 중복을 제거하고 부족한 숫자를 채워주는 함수
def remove_duplicates_and_fill(predicted_numbers):
    unique_numbers = list(set(predicted_numbers))
    while len(unique_numbers) < 6:
        new_number = np.random.randint(1, 46)
        if new_number not in unique_numbers:
            unique_numbers.append(new_number)
    logging.info(f"Generated unique lotto numbers: {unique_numbers}")
    return sorted(unique_numbers)

# 번호 예측 함수
def predict_lotto_numbers(lotto_numbers):
    try:
        scaled_data, scaler = scale_data(lotto_numbers)
        if scaled_data is None:
            return []
        
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

        logging.info(f"Predicted games: {predicted_games}")
        return predicted_games
    except Exception as e:
        logging.error(f"Error predicting lotto numbers: {e}")
        return []

# 로또 번호 예측 API
@app.route('/generate-lotto', methods=['GET'])
def generate_lotto():
    logging.info("Received request for lotto numbers")
    try:
        lotto_numbers = load_lotto_data(os.path.join(os.path.dirname(__file__), 'lotto_numbers.txt'))
        predictions = predict_lotto_numbers(lotto_numbers)
        logging.info(f"Sending predictions: {predictions}")
        return jsonify(numbers=predictions)
    except Exception as e:
        logging.error(f"Error in /generate-lotto endpoint: {e}")
        return jsonify(error="Error generating lotto numbers"), 500

# AWS 또는 Cloudtype에서 자동으로 적절한 포트를 사용
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Cloudtype에서 동적으로 포트를 할당
    logging.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)
