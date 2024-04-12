#!/usr/env python3
# -*- coding: UTF-8 -*-
import time
from io import BytesIO

# 导入BosClient配置文件
import sts_sample
# 导入BOS相关模块
from baidubce import exception
from baidubce.services import bos
from baidubce.services.bos import canned_acl
from baidubce.services.bos.bos_client import BosClient
from PIL.Image import Image
from flask import Flask, request, send_file, make_response
from flask_cors import CORS
import json
import random
import requests
import cv2
from paddleocr import PaddleOCR, PPStructure
ocr_engine = PaddleOCR()
table_engine = PPStructure(layout=False)
from infer_pp_ocrv4 import infer_pp_ocrv4
from flask import Flask, request, jsonify
from PIL import Image
from io import BytesIO
import time
import io
import hashlib
import base64

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://yiyan.baidu.com"}})

wordbook = []

def make_json_response(data, status_code=200):
    response = make_response(json.dumps(data), status_code)
    response.headers["Content-Type"] = "application/json"
    return response

def upload_to_bos(image):
    bos_client = BosClient(sts_sample.config)
    imageo = Image.open(image)

    # 将图像转换为字符串
    with BytesIO() as buffer:
        imageo.save(buffer, format=imageo.format)
        image_string = buffer.getvalue()

    filename = image.filename
    timestamp = str(time.time())

    bucket_name = "plugin-develop"
    object_key = "imageTemp/" + timestamp + filename

    bos_client.put_object_from_string(bucket_name, object_key, image_string)
    timestamp = int(time.time())

    expiration_in_seconds = -1

    url = bos_client.generate_pre_signed_url(bucket_name, object_key, timestamp, expiration_in_seconds)
    return url

@app.route("/imgs/medicalLogo.jpg")
async def plugin_logo():
    """
        注册用的：返回插件的logo，要求48 x 48大小的png文件.
        注意：API路由是固定的，事先约定的。
    """
    return send_file('imgs/medicalLogo.jpg', mimetype='image/jpg')

@app.route("/examples.yaml")
async def plugin_examples():
    """
        注册用的：返回插件的examples。
    """
    with open("examples.yaml", encoding="utf-8") as f:
        text = f.read()
        return text, 200, {"Content-Type": "text/yaml"}


@app.route("/.well-known/ai-plugin.json")
async def plugin_manifest():
    """
        注册用的：返回插件的描述文件，描述了插件是什么等信息。
        注意：API路由是固定的，事先约定的。
    """
    host = request.host_url
    with open(".well-known/ai-plugin.json", encoding="utf-8") as f:
        text = f.read().replace("PLUGIN_HOST", host)
        return text, 200, {"Content-Type": "application/json"}


@app.route("/.well-known/openapi.yaml")
async def openapi_spec():
    """
        注册用的：返回插件所依赖的插件服务的API接口描述，参照openapi规范编写。
        注意：API路由是固定的，事先约定的。
    """
    with open(".well-known/openapi.yaml", encoding="utf-8") as f:
        text = f.read()
        return text, 200, {"Content-Type": "text/yaml"}

@app.route("/get_text_ocr", methods=['POST'])
async def get_text_ocr():
    """
        抽取文本图像 OCR 结果
    """
    image_file = request.files['image']
    url = upload_to_bos(image_file)
    print(url)

    # url = request.json.get('url', "")
    response = requests.get(url)
    prompt = ""
    if response.status_code == 200:
        local_img_path = "./output/tmp.jpg"
        with open(local_img_path, "wb") as file:  
            file.write(response.content)
        img = cv2.imread(local_img_path)
        if img is None:
            results = "图片路径不存在或者读取失败！"
        else:
            results = infer_pp_ocrv4(ocr_engine, local_img_path, res_delimiter="\n")
            prompt = "请将工具返回结果中的results信息提取出来，不要改写任何内容，也不要新增内容。在结果开头，加上字符串‘【OCR结果】’"     
    else:
        results = "图片路径不存在或者读取失败！"
    
    return make_json_response({"results": results, "prompt": prompt})

def get_eb_history_info(yiyan_info_ori):
    yiyan_info_ori = json.loads(yiyan_info_ori)
    eb_ocr_res_list = []
    for ino in range(len(yiyan_info_ori)):
        role = yiyan_info_ori[ino]['role']  
        content = yiyan_info_ori[ino]['content']        
        if role == 'user' and '<url>' in content:
            substr = content.split('<url>')
            url = substr[1].split('</url>')[0]
            if (ino + 1) < len(yiyan_info_ori):
                role = yiyan_info_ori[ino + 1]['role']  
                content = yiyan_info_ori[ino + 1]['content']
                if role == "assistant" and '【OCR结果】' in content:
                    substr = content.split('【OCR结果】')
                    ocr_res = substr[1]
                    eb_ocr_res_list.append([url, ocr_res])
    return eb_ocr_res_list

@app.route("/get_kie", methods=['POST'])
async def get_kie():
    """
        抽取文本图像KIE信息
    """
    yiyan_info_ori = request.json.get('yiyan_info', "")
    eb_ocr_res_list = get_eb_history_info(yiyan_info_ori)

    if len(eb_ocr_res_list) > 0:
        keys = request.json.get('keys', "")
        results = eb_ocr_res_list[0][1]
    else:
        results = "OCR结果读取失败！"
    prompt = f"请根据工具返回结果中的results信息，提取关键字段{keys}的信息，不要使用results信息之外的信息。"
    return make_json_response({"results": results, "prompt": prompt})

@app.route("/get_table_ocr", methods=['POST'])
async def get_table_ocr():
    """
        抽取表格图像 OCR 结果或信息
    """
    yiyan_info_ori = request.json.get('yiyan_info', "")
    eb_ocr_res_list = get_eb_history_info(yiyan_info_ori)

    if len(eb_ocr_res_list) > 0:
        url = eb_ocr_res_list[0][0]
        response = requests.get(url)
        if response.status_code == 200:
            local_img_path = "./output/tmp.jpg"
            with open(local_img_path, "wb") as file:  
                file.write(response.content)
            img = cv2.imread(local_img_path)
            if img is None:
                results = "图片路径不存在或者读取失败！"
            else:
                results = table_engine(img)
                results = results[0]['res']['html']
        else:
            results = "图片路径不存在或者读取失败！"
    else:
        results = "图片路径不存在或者读取失败！"
    prompt = "请将工具返回结果中的results信息提取出来，同时将图像表格html格式的结果生成一个Markdown格式的可视化表格。"
    return make_json_response({"results": results, "prompt": prompt})

@app.route("/ask_Doctor", methods=['POST'])
async def ask_Doctor():
    """
        问医生
    """
    description = request.json.get('description', "")
    prompt = (f"大模型你是一个专业的医生，现在病人已经给出了他的病情描述：{description}。请你上网搜索此病情：{description}的治疗方法，并利用专业医疗知识根据病人的描述给出一个合理的诊断结果，以及一些有用的治疗手段以及药物清单。并且希望病人能给出更多的病情信息。最后需要声明诊断结果仅供参考，"
              "不作为临床诊断依据。并鼓励患者乐观面对疾病，积极配合医生治疗。")
    return make_json_response({"results": description, "prompt": prompt})


@app.route('/')
def index():
    return 'welcome to my webpage!'

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8011)