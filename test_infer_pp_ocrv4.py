from paddleocr import PaddleOCR, PPStructure
from infer_pp_ocrv4 import infer_pp_ocrv4
import numpy as np
import cv2
ocr_engine = PaddleOCR()
table_engine = PPStructure(layout=False)
#url = "https://img0.baidu.com/it/u=734673557,2609043629&fm=253&fmt=auto&app=138&f=JPEG?w=600&h=384"
url = "https://img1.baidu.com/it/u=3377805516,1605265881&fm=253&fmt=auto&app=138&f=JPEG?w=1105&h=233"
import requests
local_img_path = "./output/tmp.jpg"
response = requests.get(url)
local_img_path = "./output/tmp.jpg"
with open(local_img_path, "wb") as file:
	file.write(response.content)
all_context = infer_pp_ocrv4(ocr_engine, local_img_path)
img = cv2.imread(local_img_path)
result = table_engine(img)
print(all_context)
print(result[0]['res']['html'])

