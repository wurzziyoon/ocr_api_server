# encoding=utf-8
import argparse
import base64
import json

import ddddocr
import re

from flask import Flask, request

from env_loader import COOKIE,PROXY
import requests
import baidu_ocr
import image_process
import cv2
import numpy as np

parser = argparse.ArgumentParser(description="使用ddddocr搭建的最简api服务")
parser.add_argument("-p", "--port", type=int, default=9898)
parser.add_argument("--ocr", action="store_true", help="开启ocr识别" , default=True)
parser.add_argument("--old", action="store_true", help="OCR是否启动旧模型")
parser.add_argument("--det", action="store_true", help="开启目标检测", default=True)

args = parser.parse_args()

app = Flask(__name__)


class Server(object):
    def __init__(self, ocr=True, det=False, old=False):
        self.ocr_option = ocr
        self.det_option = det
        self.old_option = old
        self.ocr = None
        self.det = None
        if self.ocr_option:
            print("ocr模块开启")
            if self.old_option:
                print("使用OCR旧模型启动")
                self.ocr = ddddocr.DdddOcr(old=True)
            else:
                print("使用OCR新模型启动，如需要使用旧模型，请额外添加参数  --old开启")
                self.ocr = ddddocr.DdddOcr()
        else:
            print("ocr模块未开启，如需要使用，请使用参数  --ocr开启")
        if self.det_option:
            print("目标检测模块开启")
            self.det = ddddocr.DdddOcr(det=True)
        else:
            print("目标检测模块未开启，如需要使用，请使用参数  --det开启")

    def classification(self, img: bytes):
        if self.ocr_option:
            return self.ocr.classification(img)
        else:
            raise Exception("ocr模块未开启")

    def detection(self, img: bytes):
        if self.det_option:
            return self.det.detection(img)
        else:
            raise Exception("目标检测模块模块未开启")

    def slide(self, target_img: bytes, bg_img: bytes, algo_type: str):
        dddd = self.ocr or self.det or ddddocr.DdddOcr(ocr=False)
        if algo_type == 'match':
            return dddd.slide_match(target_img, bg_img)
        elif algo_type == 'compare':
            return dddd.slide_comparison(target_img, bg_img)
        else:
            raise Exception(f"不支持的滑块算法类型: {algo_type}")

server = Server(ocr=args.ocr, det=args.det, old=args.old)

def is_valid_url(url):
    pattern = re.compile(r'^(?:http|ftp)s?://'  # http:// or https://
                         r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
                         r'localhost|'  # localhost...
                         r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                         r'(?::\d+)?'  # optional port
                         r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return pattern.match(url) is not None

def get_img(request, img_type='file', img_name='image'):
    if img_type == 'b64':
        img = base64.b64decode(request.get_data()) # 
        try: # json str of multiple images
            dic = json.loads(img)
            img = base64.b64decode(dic.get(img_name).encode())
        except Exception as e: # just base64 of single image
            pass
    elif img_type=='url':        
        url =request.get_data().decode('utf-8')
        if not is_valid_url(url):
            return None
        
        dic = {
            'headers':
            {
                "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            }
        }
        if PROXY is not None:
            dic['proxies'] = {"http":PROXY,"https":PROXY}
        if COOKIE is not None:
            dic['headers']['Cookie'] = COOKIE
        r = requests.get(url,proxies=dic['proxies'],headers=dic['headers'])
        img = bytes(r.content)
    else:
        img = request.files.get(img_name).read()
    try:
        if(request.headers["Preprocessing"] == '1'):
            img=np.asarray(bytearray(img))
            img=cv2.imdecode(img, cv2.IMREAD_COLOR)
            img=image_process._convert(img)
    except Exception as e:
        pass
    return img


def set_ret(result, ret_type='text'):
    if ret_type == 'json':
        if isinstance(result, Exception):
            return json.dumps({"status": 200, "result": "", "msg": str(result)})
        else:
            return json.dumps({"status": 200, "result": result, "msg": ""})
        # return json.dumps({"succ": isinstance(result, str), "result": str(result)})
    else:
        if isinstance(result, Exception):
            return ''
        else:
            return str(result).strip()


@app.route('/<opt>/<provider>/<img_type>', methods=['POST'])
@app.route('/<opt>/<provider>/<img_type>/<ret_type>', methods=['POST'])
@app.route('/<opt>/<ret_type>', methods=['POST'])
def ocr(opt, provider='ddddocr', img_type='file', ret_type='text'):
    try:
        img = get_img(request, img_type)
        if opt == 'ocr':
            if provider=='baidu' :
                result = baidu_ocr.recognize(img)
            else:
                result = server.classification(img)
        elif opt == 'det':
            result = server.detection(img)
        else:
            raise f"<opt={opt}> is invalid"
        return set_ret(result, ret_type)
    except Exception as e:
        return set_ret(e, ret_type)

@app.route('/slide/<algo_type>/<img_type>', methods=['POST'])
@app.route('/slide/<algo_type>/<img_type>/<ret_type>', methods=['POST'])
def slide(algo_type='compare', img_type='file', ret_type='text'):
    try:
        target_img = get_img(request, img_type, 'target_img')
        bg_img = get_img(request, img_type, 'bg_img')
        result = server.slide(target_img, bg_img, algo_type)
        return set_ret(result, ret_type)
    except Exception as e:
        return set_ret(e, ret_type)

@app.route('/ping', methods=['GET'])
def ping():
    return "pong"


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=args.port)
