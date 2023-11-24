from flask import Flask, request, jsonify
from ultralytics import YOLO
import os
import shutil

app = Flask(__name__)

# Initialize YOLO model
yolo = YOLO('mold_best.pt')

# Results folder paths
result_crops_path = 'runs/detect/predict/crops'
result_labels_path = 'runs/detect/predict/labels'

# Clear result folders
if os.path.exists(result_crops_path):
    shutil.rmtree(result_crops_path)

if os.path.exists(result_labels_path):
    shutil.rmtree(result_labels_path)

# Read mold names from file
with open('mold_name.txt', 'r', encoding='utf-8') as file:
    mold_names = file.readlines()

def map_cls_to_mold_name(cls):
    return mold_names[int(cls)].strip()

# API 엔드포인트
@app.route('/detect', methods=['POST'])
def detect():
    try:
        # Get image link from the request
        image_link = request.form.get('image_link')

        # Check if the image file exists locally
        if not os.path.exists(image_link):
            return jsonify({'error': 'Image file does not exist'}), 400

        # Perform YOLO detection
        results = yolo(image_link)

        # Extract results
        detection_cls = results[0].boxes.cls.tolist()
        detection_conf = results[0].boxes.conf.tolist()

        # Map class numbers to names
        result_list_mapped = [(map_cls_to_mold_name(detection_cls[i]), detection_conf[i]) for i in range(len(detection_cls))]

        # Sort results by confidence
        result_list_mapped.sort(key=lambda x: x[1], reverse=True)

        # Prepare response data
        response_data = [{'class': cls, 'confidence': round(conf, 4)} for cls, conf in result_list_mapped]

        return jsonify(response_data)

    except Exception as e:
        # Log the exception for debugging purposes
        print(f"An error occurred: {str(e)}")

        # Return a meaningful error response
        return jsonify({'error': 'An internal server error occurred'}), 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)


    