from flask import Flask, request, jsonify
from ultralytics import YOLO
from PIL import Image
from io import BytesIO
import base64

app = Flask(__name__)

# YOLO 모델 초기화
yolo = YOLO('mold_best.pt')

# 이미지 업로드를 위한 API 엔드포인트
@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        # 요청에서 이미지 데이터 가져오기
        image_data = request.files['image']

        # 이미지 데이터를 PIL Image로 변환
        image = Image.open(image_data)

        # YOLO 검출 수행
        results = yolo(image)

        # 결과 추출
        detection_cls = results[0].boxes.cls.tolist()
        detection_conf = results[0].boxes.conf.tolist()

        # 클래스 번호를 몰드 이름으로 매핑
        result_list_mapped = [(map_cls_to_mold_name(detection_cls[i]), detection_conf[i]) for i in range(len(detection_cls))]

        # 신뢰도에 따라 결과 정렬
        result_list_mapped.sort(key=lambda x: x[1], reverse=True)

        # 응답 데이터 준비
        response_data = [{'class': cls, 'confidence': round(conf, 4)} for cls, conf in result_list_mapped]

        return jsonify(response_data)

    except Exception as e:
        # 디버깅을 위해 예외 로그 기록
        print(f"에러 발생: {str(e)}")

        # 의미 있는 에러 응답 반환
        return jsonify({'error': '내부 서버 오류가 발생했습니다'}), 500


# Read mold names from file
with open('mold_name.txt', 'r', encoding='utf-8') as file:
    mold_names = file.readlines()
# 클래스 번호를 몰드 이름으로 매핑하는 도우미 함수
def map_cls_to_mold_name(cls):
    # mold_names가 전역으로 정의되어 있다고 가정
    return mold_names[int(cls)].strip()

if __name__ == '__main__':
    app.run(debug=True)
