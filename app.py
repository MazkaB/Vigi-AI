from flask import Flask, request, render_template, jsonify, send_file
import os
import cv2
from roboflow import Roboflow
import tempfile

app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Initialize Roboflow with your API key
rf = Roboflow(api_key="lXZdRDe1SPy3KUdnj2G3")
project = rf.workspace().project("cc-tv-footage-annotation-b8-mx25p")
model = project.version(4).model

@app.route('/')
def index():
    # Serve the application.html from the current directory
    return send_file('application.html')

@app.route('/<path:path>')
def send_static(path):
    return send_file(os.path.join(app.static_folder, path))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        
        # Process the video
        output_filename = process_video(filename)
        
        return jsonify({'success': True, 'output': output_filename})

def process_video(video_path):
    video_capture = cv2.VideoCapture(video_path)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    output_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'output.avi')
    out = cv2.VideoWriter(output_filename, fourcc, 20.0, (int(video_capture.get(3)), int(video_capture.get(4))))

    while video_capture.isOpened():
        ret, frame = video_capture.read()
        if not ret:
            break

        # Run inference using numpy array
        prediction = model.predict(frame, confidence=50, overlap=30)

        # Draw predictions on the frame
        for item in prediction.json()['predictions']:
            x_center = int(item['x'])
            y_center = int(item['y'])
            width = int(item['width'])
            height = int(item['height'])
            class_label = item['class']
            confidence = item['confidence']

            x1 = int(x_center - width / 2)
            y1 = int(y_center - height / 2)
            x2 = int(x_center + width / 2)
            y2 = int(y_center + height / 2)

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{class_label} {confidence:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Write the frame with annotations
        out.write(frame)

    video_capture.release()
    out.release()
    cv2.destroyAllWindows()

    return output_filename

if __name__ == '__main__':
    app.run(debug=True)
