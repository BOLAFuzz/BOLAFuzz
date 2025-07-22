# -*-coding:utf-8 -*-
import ddddocr
import requests

ocr_driver = ddddocr.DdddOcr()


def identify(url, session):
    # 通过验证码链接下载图片并用ddddocr进行识别
    req = requests.Request(method='GET', url=url)
    resp = session.send(session.prepare_request(req), verify=False, timeout=3)
    tmp_save_file = '../temp/' + url.split('://')[1].split('/')[
        0].replace('.', '-') + '.png'

    if resp.status_code == 200:
        with open(tmp_save_file, 'wb') as file:
            file.write(resp.content)
        print('[+] 验证码获取成功, 保存为: ' + tmp_save_file)
    else:
        print(f'[!] 验证码获取失败, 状态码为: {resp.status_code}')

    with open(tmp_save_file, 'rb') as f:
        captcha_img = f.read()
    captcha_res = ocr_driver.classification(captcha_img)

    return captcha_res
