from flask import Flask, render_template, Response, url_for
from camera import VideoCamera

app = Flask(__name__)

i = 0

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/recording")
def recording():
    return render_template("video.html")

def gen(camera):
    while True:
        frame = camera.getFrame()
        yield (b'--frame\r\n'
               b'Content-type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    global i
    i = i + 1
    return Response(gen(VideoCamera(i)), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run()