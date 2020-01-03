import numpy as np
import cv2
from datetime import datetime

def getDateTime():
    dateTimeObj = datetime.now()
    return str(dateTimeObj.year) + '/' + str(dateTimeObj.month) + '/' + str(dateTimeObj.day) + ' ' + str(
        dateTimeObj.hour) + ':' + str(dateTimeObj.minute) + ':' + str(dateTimeObj.second)

class VideoCamera(object):

    def __init__(self, nb):
        self.sdThresh = 10
        self.font = cv2.FONT_HERSHEY_SIMPLEX

        self.frame1 = None
        self.frame2 = None

        self.videoNo = nb

        self.oVideoWriter = None

        #capture video stream from camera source. 0 refers to first camera, 1 referes to 2nd and so on.
        self.cap = cv2.VideoCapture(0)

        self.WIDTH = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.HEIGHT = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        self.thresholdImg = None

        print(str(self.WIDTH) + ' ' + str(self.HEIGHT))

    def writeTextOnFrame(self, text, frame, x, y, size, weight, color):
        cv2.putText(frame, text, (x, y), self.font, size, color, weight, cv2.LINE_AA)

    def computeDifference(self):
        _, self.frame1 = self.cap.read()
        # turn the frames to gray scale
        gray1 = cv2.cvtColor(self.frame1, cv2.COLOR_BGR2GRAY)

        _, self.frame2 = self.cap.read()
        gray2 = cv2.cvtColor(self.frame2, cv2.COLOR_BGR2GRAY)

        # compute the absolute difference between the 2 frames
        dist = cv2.absdiff(gray1, gray2)

        # make the dist frame all black and white
        _, self.thresholdImg = cv2.threshold(dist, 20, 255, cv2.THRESH_BINARY)

        # apply blur to get rid of noise
        self.thresholdImg = cv2.GaussianBlur(dist, (9, 9), 0)

        # make it black and white again (obtain binary image)
        _, self.thresholdImg = cv2.threshold(self.thresholdImg, 20, 255, cv2.THRESH_BINARY)

        # calculate the standard deviation
        _, stDev = cv2.meanStdDev(self.thresholdImg)

        return stDev

    def __del__(self):
        self.beep.stop()
        self.cap.release()
        cv2.destroyAllWindows()

    def createVideoFile(self):
        self.oVideoWriter = cv2.VideoWriter('D:/sscWorkspace/motionDetection/recordings/MyVideo' + str(self.videoNo) + '.avi', cv2.VideoWriter_fourcc(*'XVID'), 20.0, (int(self.WIDTH), int(self.HEIGHT)))
        if not self.oVideoWriter.isOpened():
            print("failed to initialize video")

    def detectMotion(self):
        if self.computeDifference() > self.sdThresh:
            return True
        else:
            return False

    def writeVideoFile(self):
        if not self.oVideoWriter:
            self.createVideoFile()
        date_time = getDateTime()
        self.writeTextOnFrame(date_time, self.frame2, 0, int(self.HEIGHT) - 15, 0.5, 1, (255, 255, 255))
        self.oVideoWriter.write(self.frame1)
        self.oVideoWriter.write(self.frame2)

    def getFrame(self):
        motion = self.detectMotion()
        date_time = getDateTime()
        self.writeTextOnFrame(date_time, self.frame1, 0, int(self.HEIGHT) - 15, 0.5, 1, (255, 255, 255))

        if motion:
            self.writeVideoFile()
            self.writeTextOnFrame('REC.', self.frame1, 0, 30, 1, 3, (0, 0, 255))
            self.writeTextOnFrame('MOTION DETECTED', self.frame1, int(self.WIDTH) - 300, int(self.HEIGHT) - 15, 1, 1, (0, 255, 0))

        _, image = cv2.imencode('.jpeg', self.frame1)

        return image.tostring()

