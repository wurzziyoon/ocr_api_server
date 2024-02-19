import re

from aip import AipOcr

from env_loader import APP_ID, API_KEY, SECRET_KEY,PROXY

MAX_RETRY = 5

ocr_client = AipOcr(APP_ID, API_KEY, SECRET_KEY)


def recognize(png_cv_bytes):
    result_json = ocr_client.basicGeneral(png_cv_bytes)
    if 'error_code' in result_json:
        # failed
        result_code = ''
    else:
        result_code = result_json['words_result'][0]['words']
        result_code = re.sub(r'[\W_]+', '', result_code)  # 只保留字母和数字
        result_code = result_code.upper()  # 只有大写字母

    return result_code
