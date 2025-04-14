
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10-blue?logo=python" />
  <img src="https://img.shields.io/badge/Flask-API-lightgrey?logo=flask" />
  <img src="https://img.shields.io/badge/LSTM-Prediction-orange?logo=tensorflow" />
  <img src="https://img.shields.io/badge/DeepLearning-Keras-red?logo=keras" />
</p>

# 🎯 Lotto Number Prediction – LSTM 기반 로또 번호 예측 API

> LSTM 딥러닝 모델을 기반으로, 과거 회차 데이터를 학습하여 다음 회차의 로또 번호를 예측하는 Flask REST API입니다.

---

## 🌟 특징

- ✅ **LSTM 모델 기반 예측**: 과거 60회차의 데이터를 분석해 다음 회차의 번호를 생성합니다.
- ✅ **중복 제거 및 범위 보정**: 예측된 번호는 1~45 범위로 보정하고, 중복되지 않게 구성됩니다.
- ✅ **회차 자동 계산**: 현재 시간에 따라 최신 회차 정보를 동적으로 계산합니다.
- ✅ **프론트엔드 연동 가능**: CORS 설정을 통해 `https://llt-aws.vercel.app`에서 안전하게 호출 가능합니다.
- ✅ **헬스 체크 API 포함**: 서버 상태 및 모델/데이터 파일 존재 여부 확인 가능

---

## 🧠 주요 예측 로직 (predict.py)

```python
# 데이터 정규화
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(lotto_numbers)

# 입력 시퀀스 생성 (60회차 기준)
x_test = np.array([scaled_data[-60:]])

# 예측 및 후처리
predicted = model.predict(x_test)
predicted = scaler.inverse_transform(predicted)
predicted = np.clip(np.around(predicted).astype(int), 1, 45)
```

> 🎲 예측 결과는 총 5게임이며, 각 게임은 6개의 번호로 구성됩니다.

---

## 🔌 API 사용법

### 🎯 로또 번호 예측
```
GET /generate-lotto
```

**응답 예시:**
```json
{
  "numbers": [
    [8, 11, 18, 27, 33, 40],
    [3, 7, 19, 24, 36, 42]
  ],
  "round": 1122
}
```

### ❤️ 헬스 체크
```
GET /health
```

**응답 예시:**
```json
{
  "status": "healthy",
  "timestamp": "2025-04-14T10:10:00",
  "service": "lotto-prediction-api",
  "checks": {
    "model_file": true,
    "data_file": true
  }
}
```

---

## 🚀 실행 방법

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 서버 실행
python app.py
```

> 기본 포트는 `5000`이며, 필요 시 환경 변수로 변경 가능합니다.

---

## 📌 예측 데이터 포맷 (lotto_numbers.txt)

```
1120,3,7,11,24,35,41
1121,6,13,17,23,29,44
```

---

## 🔒 보안 및 배포 팁

- 프론트엔드 도메인 외 접근은 CORS로 제한되어 있습니다.
- 모델 파일(`lotto_model.h5`) 및 데이터 파일(`lotto_numbers.txt`)의 보안을 유지하세요.
- Flask 서버는 ngrok, Cloudtype 등을 활용해 배포할 수 있습니다.

---

## 🙌 크레딧

- [TensorFlow](https://www.tensorflow.org/)
- [Keras](https://keras.io/)
- [Flask](https://flask.palletsprojects.com/)
- [NumPy](https://numpy.org/)
- [Scikit-learn](https://scikit-learn.org/)

---

<p align="center">
  <b>LSTM 로또 번호 예측기 🎲</b><br/>
  <em>학습용 프로젝트로 재미와 실험을 위해 제작된 예측 시스템입니다.</em>
</p>
