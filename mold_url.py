# from flask import Flask, request, jsonify
# from ultralytics import YOLO
# import os
# import shutil

# app = Flask(__name__)

# # Initialize YOLO model
# yolo = YOLO('mold_best.pt')

# # Results folder paths
# result_crops_path = 'runs/detect/predict/crops'
# result_labels_path = 'runs/detect/predict/labels'

# # Clear result folders
# if os.path.exists(result_crops_path):
#     shutil.rmtree(result_crops_path)

# if os.path.exists(result_labels_path):
#     shutil.rmtree(result_labels_path)

# # Read mold names from file
# with open('mold_name.txt', 'r', encoding='utf-8') as file:
#     mold_names = file.readlines()

# def map_cls_to_mold_name(cls):
#     return mold_names[int(cls)].strip()

# # API 엔드포인트
# @app.route('/detect', methods=['POST'])
# def detect():
#     try:
#         # Get image link from the request
#         image_link = request.form.get('image_link')

#         # Check if the image file exists locally
#         if not os.path.exists(image_link):
#             return jsonify({'error': 'Image file does not exist'}), 400

#         # Perform YOLO detection
#         results = yolo(image_link)

#         # Extract results
#         detection_cls = results[0].boxes.cls.tolist()
#         detection_conf = results[0].boxes.conf.tolist()

#         # Map class numbers to names
#         result_list_mapped = [(map_cls_to_mold_name(detection_cls[i]), detection_conf[i]) for i in range(len(detection_cls))]

#         # Sort results by confidence
#         result_list_mapped.sort(key=lambda x: x[1], reverse=True)

#         # Prepare response data
#         response_data = [{'class': cls, 'confidence': round(conf, 4)} for cls, conf in result_list_mapped]

#         return jsonify(response_data)

#     except Exception as e:
#         # Log the exception for debugging purposes
#         print(f"An error occurred: {str(e)}")

#         # Return a meaningful error response
#         return jsonify({'error': 'An internal server error occurred'}), 500

# if __name__ == '__main__':
#     app.run(debug=True, host="0.0.0.0", port=5000)


#     # http://3.34.185.44:5000/detect



# 파일에서 이름을 읽어옵니다.
from flask import Flask, request, jsonify
from ultralytics import YOLO
import os
import shutil
from werkzeug.utils import secure_filename
import base64
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app)  # 모든 엔드포인트에 대한 CORS를 활성화합니다.
app = Flask(__name__)
@app.route('/')
def home():
    return 'Hello, this is the home page!'
# API 엔드포인트
@app.route('/detect', methods=['POST'])
def detect():
    try:
        # POST 요청에 파일 부분이 있는지 확인합니다.
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        version = request.form.get('version')  # 요청에서 'version' 값을 읽어옵니다.

        # 파일이 비어있는지 확인합니다.
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # 버전에 따라 적절한 모델과 파일 이름을 선택합니다.
        if version == 'mold':
            model_file = 'mold_best.pt'
            name_file = 'mold_name.txt'
        elif version == 'bacteria':
            model_file = 'bacteria_best.pt'
            name_file = 'bacteria_name.txt'
        else:
            return jsonify({'error': 'Invalid version'}), 400

        # 파일에서 이름을 읽어옵니다.
        with open(name_file, 'r', encoding='utf-8') as file:
            mold_names = file.readlines()

        def map_cls_to_mold_name(cls):
            return mold_names[int(cls)].strip()

        # 업로드된 파일을 임시 위치에 저장합니다.
        filename = secure_filename(file.filename)
        file_path = os.path.join('temp_uploads', filename)
        file.save(file_path)

        # YOLO 감지 수행
        yolo = YOLO(model_file)
        results = yolo(file_path)

        # 결과 추출
        detection_cls = results[0].boxes.cls.tolist()
        detection_conf = results[0].boxes.conf.tolist()

        # 클래스 번호를 이름으로 매핑
        result_list_mapped = [(map_cls_to_mold_name(detection_cls[i]), detection_conf[i]) for i in range(len(detection_cls))]

        # 확률에 따라 결과 정렬
        result_list_mapped.sort(key=lambda x: x[1], reverse=True)

        # 응답 데이터 준비
        response_data = [{'version': version, 'class': cls, 'confidence': round(conf, 4)} for cls, conf in result_list_mapped]

        # 처리가 끝난 후 임시 파일 삭제
        os.remove(file_path)

        return jsonify(response_data)

    except Exception as e:
        # 디버깅을 위해 예외를 로그에 기록합니다.
        print(f"오류 발생: {str(e)}")

        # 의미 있는 오류 응답 반환
        return jsonify({'error': '내부 서버 오류가 발생했습니다.'}), 500

if __name__ == '__main__':
    # 'temp_uploads' 폴더가 존재하는지 확인하고 없으면 생성합니다.
    os.makedirs('temp_uploads', exist_ok=True)

    app.run(debug=True, host="0.0.0.0", port=5000)