#!/usr/env python3
# -*- coding: UTF-8 -*-

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
2
#
import os
#

app = Flask(__name__)
os.chdir("D:\Projections\BaiduOD\pp-chatocr")

CORS(app, resources={r"/*": {"origins": "https://yiyan.baidu.com"}})

wordbook = []

def make_json_response(data, status_code=200):
    response = make_response(json.dumps(data), status_code)
    response.headers["Content-Type"] = "application/json"
    return response


@app.route("/get_text_ocr", methods=['POST'])
async def get_text_ocr():
    """
        抽取文本图像 OCR 结果
    """
    url = request.json.get('url', "")
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

@app.route("/imgs/ocr.png")
async def plugin_logo():
    """
        注册用的：返回插件的logo，要求48 x 48大小的png文件.
        注意：API路由是固定的，事先约定的。
    """
    return send_file('imgs/ocr.png', mimetype='image/png')

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


@app.route('/')
def index():
    return 'welcome to my webpage!'

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8080,ssl_context=('certificate.crt','private.key') )

    
