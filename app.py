from flask import Flask, request, flash, redirect, url_for, render_template, Response
import subprocess
import os
import time
from werkzeug.utils import secure_filename
import cv2

app = Flask(__name__)
app.secret_key = "super_secret_stream_key_123"

UPLOAD_FOLDER = "static/videos"
ALLOWED_EXTENSIONS = {"mp4", "avi", "mkv", "mov"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
def generate_frames():
    camera = cv2.VideoCapture(0)  # Use 0 for default webcam
    while True:
        success, frame = camera.read()
        if not success:
            break
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    camera.release()



def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/add_stream", methods=["POST"])
def add_stream():
    print("POST request received")
    if "video_file" not in request.files:
        flash("No file uploaded")
        return redirect(url_for("index"))

    video = request.files["video_file"]
    print("Received file:", video.filename)
    stream_key = request.form.get("stream_key")

    if video.filename == "":
        flash("No selected file")
        return redirect(url_for("index"))

    if not allowed_file(video.filename):
        flash("Invalid video format. Only mp4, avi, mkv, mov allowed")
        return redirect(url_for("index"))

    # sanitize filename
    filename = secure_filename(video.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    print("Saving file to:", file_path)

    video.save(file_path)

    if not os.path.exists(file_path):
        flash("Video failed to save")
        return redirect(url_for("index"))

    print("Video saved successfully")

    time.sleep(1)

    # FFmpeg command
    command = [
        "ffmpeg",
        "-re",
        "-stream_loop", "-1",
        "-i", file_path,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-maxrate", "3000k",
        "-bufsize", "6000k",
        "-pix_fmt", "yuv420p",
        "-g", "50",
        "-c:a", "aac",
        "-b:a", "160k",
        "-f", "flv",
        f"rtmp://a.rtmp.youtube.com/live2/{stream_key}",
    ]

    print("Starting FFmpeg stream...")
    print(" ".join(command))

    # start streaming without blocking flask
    subprocess.Popen(command)

    flash("Stream started successfully")

    return redirect(url_for("index"))
@app.route("/live_stream", methods=["POST"])
def live_stream():

    stream_key = request.form.get("stream_key")

    if not stream_key:
        flash("Stream key is required")
        return redirect(url_for("index"))

    command = [
        "ffmpeg",

        "-f", "v4l2",
        "-framerate", "24",
        "-video_size", "640x480",
        "-i", "/dev/video0",

        "-f", "lavfi",
        "-i", "anullsrc",

        "-c:v", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",

        "-c:a", "aac",

        "-f", "flv",
        f"rtmp://a.rtmp.youtube.com/live2/{stream_key}",
    ]

    print("Starting LIVE webcam stream...")
    print(" ".join(command))

    subprocess.Popen(command)

    flash("Live webcam stream started!")

    return redirect(url_for("index"))
    

@app.route('/webcam')
def webcam_display():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
