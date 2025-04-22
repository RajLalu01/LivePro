from flask import Flask, request, render_template
import os
import subprocess

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
process = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start-stream', methods=['POST'])
def start_stream():
    global process
    video = request.files['video']
    stream_key = request.form['stream_key']
    video_path = os.path.join(UPLOAD_FOLDER, video.filename)
    video.save(video_path)

    if process and process.poll() is None:
        return "Stream already running."

    command = [
        'ffmpeg',
        '-stream_loop', '-1',
        '-re',
        '-i', video_path,
        '-c:v', 'libx264',
        '-preset', 'veryfast',
        '-maxrate', '3000k',
        '-bufsize', '6000k',
        '-pix_fmt', 'yuv420p',
        '-g', '50',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-f', 'flv',
        f'rtmp://a.rtmp.youtube.com/live2/{stream_key}'
    ]

    process = subprocess.Popen(command)
    return "Stream started!"

@app.route('/stop-stream', methods=['POST'])
def stop_stream():
    global process
    if process:
        process.terminate()
        process = None
        return "Stream stopped."
    return "No stream running."

@app.route('/delete-video', methods=['POST'])
def delete_video():
    for file in os.listdir(UPLOAD_FOLDER):
        os.remove(os.path.join(UPLOAD_FOLDER, file))
    return "Video(s) deleted."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)