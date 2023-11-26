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



# # # 파일에서 이름을 읽어옵니다.
from flask import Flask, request, jsonify
from ultralytics import YOLO
import os
import shutil
from werkzeug.utils import secure_filename
import base64
from flask_cors import CORS


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Chrome, ChromeService
from selenium.webdriver.common.by import By
# app = Flask(__name__)


app = Flask(__name__)
CORS(app)  # 모든 엔드포인트에 대한 CORS를 활성화합니다.
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

        file_img = request.files['file']
        # filename = secure_filename(request.files['file'].name)
        version = request.form.get('version')  # 요청에서 'version' 값을 읽어옵니다.
        # print(f"Received file: {file.name}")
        # print(f"Received version: {version}")
        # 파일이 비어있는지 확인합니다.
        # if file_img.name == '':
        #     return jsonify({'error': 'No selected file'}), 400

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
        
        file_path = os.path.join('temp_uploads', secure_filename(file_img.filename))
        file_img.save(file_path)

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

        # /////////////////////////////////////////////
        # 현재 작업 디렉토리 확인
        current_directory = os.getcwd()

        # 웹 드라이버 생성 (executable_path 대신에 options를 사용)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')  # 특정 환경에서 필요할 수 있습니다
        # chrome_options.add_argument('--headless')  # 실행 중에 브라우저 창을 표시하지 않음

        # chromedriver 실행 파일의 경로 설정
        # chrome_options.binary_location = os.path.join(current_directory)

        # driver = webdriver.Chrome(options=chrome_options)

        # # 웹 드라이버 파일이 현재 작업 디렉토리에 위치한다고 가정하고 경로 설정
        # driver_path = os.path.join(current_directory, 'chromedriver')

        # # 웹 드라이버 생성
        # driver = webdriver.Chrome(executable_path=driver_path)

        # 크롤링을 위한 루프
        result_texts = []

        for i, (cls, conf) in enumerate(result_list_mapped):
            print(f"Processing item {i + 1}: {cls}")

            title = cls
            if title == 'penicillum crustosum':
    #         print('title초기',title)
              title = 'penicillium crustosum'
    #         print('title변경',title)
            # 크롤링할 페이지 URL
            url = 'https://en.wikipedia.org/wiki/' + title

            driver = Chrome(service=ChromeService("chromedriver.exe"))

            # 웹 페이지 열기
            driver.get(url)

            result_text = ""

            try:
                # table 태그의 class가 "infobox"인 태그 선택
                infobox_table = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//table[contains(@class, "infobox")]'))
                )

                # infobox_table 태그와 해당 태그 사이에 있는 모든 p 태그 선택
                p_tags = infobox_table.find_elements(By.XPATH, './following-sibling::p[following-sibling::h2]')

                # 각 p 태그의 텍스트 내용을 변수에 추가
                for p_tag in p_tags:
                    result_text += p_tag.text + "\n"

                # Append the result_text to the list
                result_texts.append(result_text)

            finally:
                # 브라우저 닫기
                driver.quit()

        # /////////////////////////////////////////////

        # # 응답 데이터 준비
        # response_data = [
        #     {
        #         'version': version,
        #         'class': cls,
        #         'confidence': round(conf, 4),
        #         'result_text': result_text
        #     } for (cls, conf, result_text) in zip(result_list_mapped, result_texts)
        # ]
        response_data = []
        for (cls, conf), result_text in zip(result_list_mapped, result_texts):
            item_data = {'version': version, 'class': cls, 'confidence': round(conf, 4), 'result_text': result_text}
            response_data.append(item_data)

        # 처리가 끝난 후 임시 파일 삭제
        os.remove(file_path)

        return jsonify(response_data)

    #     # YOLO 감지 수행
    #     yolo = YOLO(model_file)
    #     results = yolo(file_path)

    #     # 결과 추출
    #     detection_cls = results[0].boxes.cls.tolist()
    #     detection_conf = results[0].boxes.conf.tolist()
    #      # 클래스 번호를 이름으로 매핑
    #     result_list_mapped = [(map_cls_to_mold_name(detection_cls[i]), detection_conf[i]) for i in range(len(detection_cls))]

    #     # 확률에 따라 결과 정렬
    #     result_list_mapped.sort(key=lambda x: x[1], reverse=True)

    #     # /////////////////////////////////////////////
    #   # 현재 작업 디렉토리 확인
    #     current_directory = os.getcwd()

    #     # 웹 드라이버 생성 (executable_path 대신에 options를 사용)
    #     chrome_options = webdriver.ChromeOptions()
    #     chrome_options.add_argument('--no-sandbox')  # 특정 환경에서 필요할 수 있습니다
    #     # chrome_options.add_argument('--headless')  # 실행 중에 브라우저 창을 표시하지 않음

    #     # chromedriver 실행 파일의 경로 설정
    #     # chrome_options.binary_location = os.path.join(current_directory)

    #     # driver = webdriver.Chrome(options=chrome_options)

    #     # # 웹 드라이버 파일이 현재 작업 디렉토리에 위치한다고 가정하고 경로 설정
    #     # driver_path = os.path.join(current_directory, 'chromedriver')

    #     # # 웹 드라이버 생성
    #     # driver = webdriver.Chrome(executable_path=driver_path)
        
    #     title = result_list_mapped[0][0]
    #     # 크롤링할 페이지 URL
    #     if title == 'penicillum crustosum':
    #         print('title초기',title)
    #         title = 'penicillium crustosum'
    #         print('title변경',title)
        
    #     url = 'https://en.wikipedia.org/wiki/'+title
    #     driver = Chrome(service = ChromeService("chromedriver.exe"))

    #     # 웹 페이지 열기
    #     driver.get(url)

    #     result_text = ""

    #     try:
    #         # table 태그의 class가 "infobox"인 태그 선택
    #         infobox_table = WebDriverWait(driver, 10).until(
    #             EC.presence_of_element_located((By.XPATH, '//table[contains(@class, "infobox")]'))
    #         )

    #         # infobox_table 태그와 해당 태그 사이에 있는 모든 p 태그 선택
    #         p_tags = infobox_table.find_elements(By.XPATH, './following-sibling::p[following-sibling::h2]')

    #         # 각 p 태그의 텍스트 내용을 변수에 추가
    #         for p_tag in p_tags:
    #             result_text += p_tag.text + "\n"

    #     finally:
    #         # 브라우저 닫기
    #         driver.quit()

    #     # 결과 출력
    #     print(result_text)
    #     # /////////////////////////////////////////////

       

    #     # 응답 데이터 준비
    #     response_data = [{'version': version, 'class': cls, 'confidence': round(conf, 4), 'result_text':result_text} for cls, conf in result_list_mapped]

    #     # 처리가 끝난 후 임시 파일 삭제
    #     os.remove(file_path)

    #     return jsonify(response_data)

    except Exception as e:
        # 디버깅을 위해 예외를 로그에 기록합니다.
        print(f"오류 발생: {str(e)}")

        # 의미 있는 오류 응답 반환
        return jsonify({'error': '내부 서버 오류가 발생했습니다.'}), 500

if __name__ == '__main__':
    # 'temp_uploads' 폴더가 존재하는지 확인하고 없으면 생성합니다.
    os.makedirs('temp_uploads', exist_ok=True)

    app.run(debug=True, host="0.0.0.0", port=5000)