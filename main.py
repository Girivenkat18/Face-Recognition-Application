import cv2 as cv
import os
import pickle
import numpy as np
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendance-2ab52-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendance-2ab52.appspot.com"
})

bucket = storage.bucket()


cam = cv.VideoCapture(1)
cam.set(3, 640)
cam.set(4, 480)
# cv.resizeWindow("cam", 720, 200)

imgBg = cv.imread('Resources/background.png')

# importing the mode images into a list
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
modePathList = modePathList[1:]
modePathList.sort()
imgModeList = []

for path in modePathList:
    imgModeList.append(cv.imread(os.path.join(folderModePath, path)))

# print(modePathList)
# print(len(imgModeList))

# loading the encoding file
print("Loading encoding file")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
print("Loaded encoding file")
# print(studentIds)

modeType = 0
counter = 0
id = -1
imgStudent = []

while True:
    success, img = cam.read()

    imgS = cv.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv.cvtColor(imgS, cv.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBg[162:162+480, 55:55+640] = img
    imgBg[44:44+633, 808:808+414] = imgModeList[modeType]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print("matches", matches)
            # print("faceDis", faceDis)


            matchIndex = np.argmin(faceDis)
            print(np.min(faceDis))
            print("Match Index", matchIndex)

            if np.min(faceDis) < 0.48:
                print("Known Face Detected")

                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBg = cvzone.cornerRect(imgBg, bbox, rt=0)
                id = studentIds[matchIndex]

                if counter == 0:
                    cvzone.putTextRect(imgBg, "Loading", (275, 400))
                    cv.imshow("Face Attendance", imgBg)
                    # cv.waitKey(1)
                    counter = 1
                    modeType = 1

            else:
                print("Not Known")
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBg = cvzone.cornerRect(imgBg, bbox, rt=0)
                imgBg[44:44 + 633, 808:808 + 414] = imgModeList[4]


            # cv.waitKey(1000)


        if counter != 0:

            if counter == 1:
                # Getting the data
                studentInfo = db.reference(f'Students/{id}').get()
                # print(studentInfo)

                # Getting image from storage
                blob = bucket.get_blob(f'Images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv.imdecode(array, cv.COLOR_BGRA2BGR)

                # updating data of attendance
                datetimeObject = datetime.strptime(studentInfo['Last Attendance Time'], "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                # print(secondsElapsed)

                if secondsElapsed > 15:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['Total Attendance'] += 1
                    ref.child('Total Attendance').set(studentInfo['Total Attendance'])
                    ref.child('Last Attendance Time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBg[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            if modeType != 3:

                if 50 < counter < 100:
                    modeType = 2

                imgBg[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                if counter <= 50:

                    cv.putText(imgBg, str(studentInfo['Total Attendance']), (861, 125), cv.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255),
                               1)

                    cv.putText(imgBg, str(studentInfo['Major']), (1006, 550), cv.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255),
                               1)

                    cv.putText(imgBg, str("221100"+id), (1006, 493), cv.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255),
                               1)

                    cv.putText(imgBg, str(studentInfo['Standing']), (910, 625), cv.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100),
                               1)

                    cv.putText(imgBg, str(studentInfo['Present Year']), (1025, 625), cv.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100),
                               1)

                    cv.putText(imgBg, str(studentInfo['Starting Year']), (1125, 625), cv.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100),
                               1)

                    (w, h), _ = cv.getTextSize(studentInfo['Name'], cv.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414-w)//2

                    cv.putText(imgBg, str(studentInfo['Name']), (808+offset, 445), cv.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50),
                               1)

                    imgBg[175:175+216, 909:909+216] = imgStudent

                counter += 1

                if counter >= 100:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    imgBg[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0

    # cv.imshow("Web Cam", img)
    cv.imshow("Face Attendance", imgBg)
    cv.waitKey(1)
