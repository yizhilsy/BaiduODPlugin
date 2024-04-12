# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
################################################################################
#
# Copyright (c) 2023 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
Author: PaddlePaddle Authors
"""
import numpy as np
import cv2
import copy

def trans_poly_to_bbox(poly):
    x1 = int(np.min([p[0] for p in poly]))
    x2 = int(np.max([p[0] for p in poly]))
    y1 = int(np.min([p[1] for p in poly]))
    y2 = int(np.max([p[1] for p in poly]))
    return [x1, y1, x2, y2]

def order_by_tbyx(ocr_info):
    # sort using y1 first and then x1
    res = sorted(ocr_info, key=lambda r: (r["bbox"][1], r["bbox"][0]))
    
    for i in range(len(res) - 1):
        for j in range(i, 0, -1):
            bbox1 = res[j + 1]["bbox"]
            bbox2 = res[j]["bbox"]
            bbox_height1 = bbox1[3] - bbox1[1] + 1
            bbox_height2 = bbox2[3] - bbox2[1] + 1
            bbox_height_pub = min(bbox1[3], bbox2[3]) - max(bbox1[1], bbox2[1])
            # restore the order using the
            if bbox_height_pub * 1.0 / bbox_height1 >= 0.5 and \
                     (res[j + 1]["bbox"][0] < res[j]["bbox"][0]):
                tmp = copy.deepcopy(res[j])
                res[j] = copy.deepcopy(res[j + 1])
                res[j + 1] = copy.deepcopy(tmp)
            else:
                break
    return res


def infer_pp_ocrv4(ocr_engine, img_path, res_delimiter="\n"):
    ocr_result = ocr_engine.ocr(img_path, cls=False)[0]
    ocr_info = []
    for res in ocr_result:
        ocr_info.append({
            "transcription": res[1][0],
            "bbox": trans_poly_to_bbox(res[0]),
            "points": res[0],
        })
    ocr_res = order_by_tbyx(ocr_info)
    txts = [res['transcription'] for res in ocr_res]
    if len(txts) > 0:
        all_context = txts[0]
        for tno in range(1, len(txts)):
            all_context = all_context + res_delimiter + txts[tno]
    else:
        all_context = ""
    return all_context
