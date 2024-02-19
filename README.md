# ocr_api_server
使用ddddocr的最简api搭建项目，支持docker

**建议python版本3.7-3.9 64位**


## 基于sml2h3/ocr_api_server & eric1932/HDSky_captcha_helper修改
* 可通过url拉取图片
* 通过ocr中的provider可以选择免费的ddddocr或者百度ocr，可以在多次失败的情况下最后使用百度ocr保底
* 可通过header参数**Preprocessing**进行图片预处理增加识别正确率

# 运行方式

## 最简单运行方式

```shell
# 安装依赖
pip install -r requirements.txt -i https://pypi.douban.com/simple

# 运行  可选参数如下
# --port 9898 指定端口,默认为9898
# --ocr 开启ocr模块 默认开启
# --old 只有ocr模块开启的情况下生效 默认不开启
# --det 开启目标检测模式

# 最简单运行方式，只开启ocr模块并以新模型计算
python ocr_server.py --port 9898 --ocr

# 开启ocr模块并使用旧模型计算
python ocr_server.py --port 9898 --ocr --old

# 只开启目标检测模块
python ocr_server.py --port 9898  --det

# 同时开启ocr模块以及目标检测模块
python ocr_server.py --port 9898 --ocr --det

# 同时开启ocr模块并使用旧模型计算以及目标检测模块
python ocr_server.py --port 9898 --ocr --old --det

```

## docker运行方式(目测只能在Linux下部署)

```shell
git clone https://github.com/wurzziyoon/ocr_api_server.git
# docker怎么安装？百度吧

cd ocr_api_server

# 修改entrypoint.sh中的参数，具体参数往上翻，默认9898端口，同时开启ocr模块以及目标检测模块

# 编译镜像
docker build -t ocr_server:v1 .

# 运行镜像
docker run -p 9898:9898 -d \
  -e APP_ID=<YOUR_APP_ID> \
  -e API_KEY=<YOUR_API_KEY> \
  -e SECRET_KEY=<YOUR_API_SECRET> \
  -e COOKIE=<GET_URL_IMAGE_REQUEST_COOKIE> \
  -e PROXY=<GET_URL_IMAGE_REQUEST_PROXY> \
  --restart unless-stopped \
  ocr_server:v1

```

# 接口

**具体请看test_api.py文件**

```python
# 1、测试是否启动成功，可以通过直接GET访问http://{host}:{port}/ping来测试，如果返回pong则启动成功

# 2、OCR/目标检测请求接口格式：

# http://{host}:{port}/{opt}/{img_type}/{ret_type}
# opt：操作类型 ocr=OCR det=目标检测 slide=滑块（match和compare两种算法，默认为compare)
# img_type: 数据类型 file=文件上传方式 b64=base64(imgbyte)方式 默认为file方式
# ret_type: 返回类型 json=返回json（识别出错会在msg里返回错误信息） text=返回文本格式（识别出错时回直接返回空文本）

# 例子：

# OCR请求
# resp = requests.post("http://{host}:{port}/ocr/{ddddocr | baidu}/file", files={'image': image_bytes})
# resp = requests.post("http://{host}:{port}/ocr/{ddddocr | baidu}/b64/text", data=base64.b64encode(file).decode())
# resp = requests.post("http://{host}:{port}/ocr/{ddddocr | baidu}/b64/text", data='https://xxxxx.com/xxxxx')

# 目标检测请求
# resp = requests.post("http://{host}:{port}/det/file", files={'image': image_bytes})
# resp = requests.post("http://{host}:{port}/det/b64/json", data=base64.b64encode(file).decode())

# 滑块识别请求
# resp = requests.post("http://{host}:{port}/slide/match/file", files={'target_img': target_bytes, 'bg_img': bg_bytes})
# jsonstr = json.dumps({'target_img': target_b64str, 'bg_img': bg_b64str})
# resp = requests.post("http://{host}:{port}/slide/compare/b64", files=base64.b64encode(jsonstr.encode()).decode())
```
