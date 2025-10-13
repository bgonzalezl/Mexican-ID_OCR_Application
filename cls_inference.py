import pandas as pd
import numpy as np
import os
from ultralytics import YOLO
import cv2

model = YOLO(r"best.pt")

def inference_application(front):
    prediction = model.predict(front, conf=0.7, verbose=True)
    index_class = int(prediction[0].probs.top1)
    label = model.names[index_class]
    if str(label) == 'G' or str(label) == 'E':
        return str(label)
    else:
        return ''