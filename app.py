# import necessary libraries like Flask, request, jsonify, flash, redirect, url_for, render_template, subprocess
from flask import Flask, request, jsonify, flash, redirect, url_for, render_template
import subprocess, re

# declare a Flask app
app = Flask(__name__)
# set secret key for the app
app.secret = 'kajslasjkj*&*&^*YJKAHSKLJAHSKJNAKSHA78687687yjkhkshdksjhdkjh'

# index route to render index.html
@app.route('/')
def index():
    return render_template('index.html')
# add_stream route to add stream_key and video
@app.route('/add_stream', methods=['POST'])
def add_stream():
    if request.method == 'POST':
        # get stream_key and video from form
        stream_key = request.form['stream_key']
        video = request.files['video_file']
        
        # filter video format
        allowed_video_format = ['mp4', 'avi', 'mkv', 'mov']
        if video.filename.split('.')[-1] not in allowed_video_format:
            flash('Invalid video format. Only mp4, avi, mkv, mov are allowed')
            return redirect(url_for('index'))
        
        # save video into static/videos
        file_path = f'static/videos/{video.filename}'
        # modify video path to save video in static/videos folder and remove all invalid characters with _
        file_path = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', file_path)
        video.save(file_path)
        # make sure that file is saved wait until it saved
        # before running ffmpeg command
        import time
        time.sleep(2)
        # run ffmpeg command to start streaming
        # ffmpeg -re -i video_path -c copy -f flv rtmp://localhost/live/stream_name
        # youtube_rtmp_url = f'rtmp://a.rtmp.youtube.com/live2/{stream_key}'
        command = f'ffmpeg -re -i {file_path} -c copy -f flv rtmp://a.rtmp.youtube.com/live2/{stream_key}'
        # ffmpeg command to stream video to youtube
        subprocess.Popen(command, shell=True)
        return redirect(url_for('index'))

# run the app
if __name__ == '__main__':
    app.run(debug=True)