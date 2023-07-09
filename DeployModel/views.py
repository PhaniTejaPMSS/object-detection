import cv2 as cv
import imutils
import numpy as np
from django.http import HttpResponse
from django.shortcuts import render, reverse
from django.views.decorators.csrf import csrf_exempt
from matplotlib import pyplot as plt
import joblib
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from django.shortcuts import redirect
from django.conf import settings

# Load the saved model weights and configuration
loaded_model_data = joblib.load('model.pkl')
thres = loaded_model_data['thres']
classes = loaded_model_data['classes']
configFile = loaded_model_data['configFile']
weightsFile = loaded_model_data['weightsFile']

# Create the model
net = cv.dnn_DetectionModel(weightsFile, configFile)
net.setInputSize(320, 320)
net.setInputScale(1.0/127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)


@csrf_exempt
def upload_video(request):
    
    if request.method == 'POST' and request.FILES.get('video'):
        video_file = request.FILES['video']
        video_path = os.path.join(settings.STATIC_DIR, video_file.name)
        with open(video_path, 'wb') as file:
            for chunk in video_file.chunks():
                file.write(chunk)

        # Perform video processing using the saved video path
        output_path, output_path_webm = process_video(video_path)

        # Remove the uploaded video file after processing (optional)
        os.remove(video_path)

        return redirect('index_with_paths', video_path=output_path, video_path_webm=output_path_webm)

    return render(request, 'eh5v.html')


def process_video(video_path):
    cap = cv.VideoCapture(video_path)
    frame_width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    output_path_webm = os.path.join(settings.STATIC_DIR, 'output.webm')
    output_path = os.path.join(settings.STATIC_DIR, 'output.m4v')

    # Define the codec and create VideoWriter objects
    fourcc_mp4 = cv.VideoWriter_fourcc(*'mp4v')
    out_mp4 = cv.VideoWriter(output_path, fourcc_mp4, 20.0, (frame_width, frame_height))

    fourcc_webm = cv.VideoWriter_fourcc(*'VP90')
    out_webm = cv.VideoWriter(output_path_webm, fourcc_webm, 20.0, (frame_width, frame_height))

    while True:
        success, img = cap.read()
        if not success:
            break

        img = imutils.resize(img, width=frame_width, height=frame_height)

        classIds, confs, bbox = net.detect(img, confThreshold=thres)
        print(classIds, bbox)

        if len(classIds) != 0:
            for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
                cv.rectangle(img, box, color=(0, 255, 0), thickness=2)
                cv.putText(img, classes[classId - 1].upper(), (box[0] + 10, box[1] + 30),
                           cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                cv.putText(img, str(round(confidence * 100, 2)), (box[0] + 10, box[1] + 60),
                           cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

        # Write the frame into the file
        out_mp4.write(img)
        out_webm.write(img)

    # Release the VideoCapture and VideoWriter objects
    cap.release()
    out_mp4.release()
    out_webm.release()

    return output_path, output_path_webm


def index_with_paths(request, video_path, video_path_webm):
    context = {
        'video_path': video_path,
        'video_path_webm': video_path_webm
    }
    return render(request, 'eh5v.html', context)

def index(request):
    return render(request,'index.html')