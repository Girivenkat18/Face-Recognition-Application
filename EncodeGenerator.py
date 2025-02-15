import cv2 as cv
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendance-2ab52-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendance-2ab52.appspot.com"
})

# importing students images into a list
folderPath = 'Images'
pathList = os.listdir(folderPath)
# print(pathList)
pathList = pathList[1:]
# print(pathList)
imgList = []
studentIds = []

for path in pathList:
    imgList.append(cv.imread(os.path.join(folderPath, path)))
    studentIds.append(os.path.splitext(path)[0])
    # print(path)
    # print(os.path.splitext(path)[0])

    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

print(studentIds)

def findEncodings(imagesList):
    encodeList = []

    for img in imagesList:

        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

        # if img.shape[2] == 4:  # Check for 4 channels (RGBA)
        #     img = cv.cvtColor(img, cv.COLOR_BGRA2RGB)
        # elif img.shape[2] == 3:  # Check for 3 channels (BGR)
        #     img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        # elif len(img.shape) == 2:  # Check for grayscale
        #     img = cv.cvtColor(img, cv.COLOR_GRAY2RGB)

        # faceLoc = face_recognition.face_locations(img)
        # encode = face_recognition.face_encodings(img, faceLoc)

        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList

print("Encoding started...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print(encodeListKnown)
print("Encoding completed")

file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File Saved")
