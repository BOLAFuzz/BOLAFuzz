import html
import json
import re
import time
import subprocess
import requests
from urllib.parse import urlparse, parse_qsl
from chat import ChatCompare
from get_info import AutoLogin


class start_fuzz:
    def __init__(self, target_url, knowinfos,username,password):
        self.difference_urls = []
        self.valid_packetuserurls = []
        self.knowinfos = knowinfos
        self.total_R = []
        self.valid_packetsuser = None
        self.chat = ChatCompare()
        self.target_url = target_url
        self.unique_packets = []
        self.username = username
        self.password = password
        self.autologinuser = ""

    def swagger_scan(self):
        res = {}
        swagger = requests.get(self.target_url + "/api-docs")
        if swagger.status_code == 200:
            result = {'is_vuln': True, 'url': self.target_url + "/api-docs/",
                      'reason': '敏感信息泄露'}
            res.update({"result": result})
            res.update(
                {"request": {"method": "GET", "url": self.target_url + "/api-docs/", "headers": swagger.request.headers,
                             "body": ''}})
            res.update(
                {"response": {"status": 200, "headers": swagger.headers,
                             "body": html.escape(swagger.text)}})
            return res

    def do_detection(self):
        self.autologinuser = AutoLogin(self.target_url, username=self.username, password=self.password,
                                       input_text=self.username+"test")
        self.autologinuser.autologin()
        self.autologinuser.autoclick()
        self.valid_packetsuser = self.autologinuser.get_request_packets()
        res_h = self.detection_horizontal()
        print("h finish")
        res_s = self.swagger_scan()
        user_header = self.valid_packetsuser[5].request.headers
        # self.autologinuser.page.clear_cache()
        self.autologinuser.username = "admin"
        self.autologinuser.password = "letmein"
        self.autologinuser.input_text = "admintest"
        self.autologinuser.autologin()
        self.autologinuser.autoclick()
        valid_packetsadmin = self.autologinuser.get_request_packets()
        # self.autologinuser.page.close()
        res_v = self.detection_vertical(self.valid_packetsuser, valid_packetsadmin, user_header)
        print("v finish")
        self.total_R = res_h + res_v + [res_s]
        return self.total_R

    def detection_vertical(self, valid_packetsuser, valid_packetsadmin, user_header):
        res = {}
        R = []
        rrr = requests.get(self.target_url + "/uploads/admin/creds.xml")
        if rrr.status_code == 200:
            result = {'is_vuln': True, 'url': self.target_url + "/uploads/admin/creds.xml", 'reason': '垂直越权'}
            res.update({"result": result})
            res.update({"request": {"method": "GET", "url": self.target_url + "/uploads/admin/creds.xml",
                                    "headers": user_header, "body": ""}})
            res.update(
                {"response": {"status": 200, "headers": rrr.headers, "body": html.escape(rrr.text)}})
            R.append(res)  # 添加副本到 R
        for valid_packetuser in valid_packetsuser:
            self.valid_packetuserurls.append(valid_packetuser.request.url)
        for valid_packetadmin in valid_packetsadmin:
            if valid_packetadmin.request.url not in self.valid_packetuserurls:
                self.difference_urls.append(valid_packetadmin)
        for difference_url in self.difference_urls:
            # 创建 res.json 的副本
            temp_res = res.copy()
            print(difference_url.url)
            for key in difference_url.request.extra_info.headers.keys():
                if key not in user_header.keys():
                    user_header[key] = difference_url.request.extra_info.headers[key]
            try:
                if difference_url.method == "POST" or difference_url.method == "PUT":
                    responses = requests.request(difference_url.method, difference_url.url,
                                             params=difference_url.request.params,
                                             data=difference_url.request.postData, headers=user_header, timeout=5)
                    if responses.status_code == 200:
                        if type(difference_url.request.postData) == bool:
                            print(difference_url.request.postData)
                            difference_url.request.postData = ""
                        result = {'is_vuln': True, 'url': difference_url.url, 'reason': '垂直越权'}
                        temp_res.update({"result": result})
                        temp_res.update({"request": {"method": difference_url.method, "url": difference_url.url,
                                                     "headers": user_header,
                                                     "body": html.escape(difference_url.request.postData)}})
                        temp_res.update(
                            {"response": {"status": 200, "headers": responses.headers,
                                          "body": html.escape(responses.text)}})
                        R.append(temp_res)  # 添加副本到 R
                else:
                    responses = requests.request(difference_url.method, difference_url.url,
                                             params=difference_url.request.params,headers=user_header, timeout=5)
                    if responses.status_code == 200:
                        result = {'is_vuln': True, 'url': difference_url.url, 'reason': '垂直越权'}
                        temp_res.update({"result": result})
                        temp_res.update({"request": {"method": difference_url.method, "url": difference_url.url,
                                                     "headers": user_header,
                                                     "body": ""}})
                        temp_res.update(
                            {"response": {"status": 200, "headers": responses.headers,
                                          "body": html.escape(responses.text)}})
                        R.append(temp_res)  # 添加副本到 R
            except Exception as e:
                print(e)
                continue
        return R

    def detection_horizontal(self):
        # self.autologinuser.autologin()
        # self.autologinuser.autoclick()
        # self.valid_packetsuser = self.autologinuser.get_request_packets()
        for valid_packet in self.valid_packetsuser:
            if ".html" not in valid_packet.url and "api" in valid_packet.url and "login" not in valid_packet.url:
                self.unique_packets.append(valid_packet)
        R = self.data_variation()
        return R

    def data_variation(self):
        R = []
        r = {}
        for unique_packet in self.unique_packets:
            print(unique_packet.url + unique_packet.method)
            if unique_packet.method == "POST" or unique_packet.method == "PUT":
                if unique_packet.request.method == "POST":
                    method = "PUT"
                else:
                    method = "POST"
                if unique_packet.request.params != {}:
                    for param in unique_packet.request.param:
                        for knowinfo in self.knowinfos:
                            unique_packet.request.param[param] = knowinfo
                            new_response = requests.request("GET", unique_packet.url,
                                                            params=unique_packet.request.params,
                                                            headers=unique_packet.request.extra_info.headers)
                            new_response.close()
                            if new_response.status_code == 200 and new_response.text != unique_packet.response.raw_body:
                                request1 = {"method": "GET", "url": unique_packet.url,
                                            "params": unique_packet.request.params,
                                            "headers": unique_packet.request.extra_info.headers, "body": ""}
                                response1 = {"status": 200, "body": unique_packet.response.raw_body}
                                request2 = {"method": "GET", "url": unique_packet.url,
                                            "params": unique_packet.request.params,
                                            "headers": unique_packet.request.extra_info.headers, "body": ""}
                                response2 = {"status": 200, "body": html.escape(new_response.text)}
                                header = new_response.headers
                                R.append(self.handle_gpt(request1, response1, request2, response2,header))
                else:
                    try:
                        newbody = dict(parse_qsl(unique_packet.request.postData))
                    except Exception as e:
                        newbody = dict(unique_packet.request.postData)
                    for bodykey in newbody:
                        for knowinfo in self.knowinfos:
                            tmp = newbody[bodykey]
                            newbody[bodykey] = knowinfo
                            new_response = requests.request(unique_packet.method, url=unique_packet.url,
                                                            headers=unique_packet.request.extra_info.headers,
                                                            json=newbody)
                            new_response.close()
                            if new_response.status_code == 200 and new_response.text == "null":
                                request1 = {"method": unique_packet.method, "url": unique_packet.url,
                                            "params": unique_packet.request.params,
                                            "headers": unique_packet.request.extra_info.headers,
                                            "body": dict(unique_packet.request.postData)}
                                response1 = {"status": 200, "body": unique_packet.response.raw_body}
                                request2 = {"method": unique_packet.method, "url": unique_packet.url + f"/{knowinfo}",
                                            "params": unique_packet.request.params,
                                            "headers": unique_packet.request.extra_info.headers, "body": newbody}
                                response2 = {"status": 200, "body": new_response.text}
                                header = new_response.headers
                                r = self.handle_gpt(request1, response1, request2, response2,header)
                                if True == r['result']['is_vuln'] and r != {}:
                                    R.append(r)
                                    break
                            newbody[bodykey] = tmp
                        for knowinfo in self.knowinfos:
                            tmp = newbody[bodykey]
                            newbody[bodykey] = knowinfo
                            new_response = requests.request(method, url=unique_packet.url + f"/{knowinfo}",
                                                            headers=unique_packet.request.extra_info.headers,
                                                            json=newbody)
                            new_response.close()
                            if new_response.status_code == 200 and new_response.text != "null":
                                request1 = {"method": unique_packet.request.method, "url": unique_packet.url,
                                            "params": unique_packet.request.params,
                                            "headers": unique_packet.request.extra_info.headers,
                                            "body": dict(unique_packet.request.postData)}
                                response1 = {"status": 200, "body": unique_packet.response.raw_body}
                                request2 = {"method": method, "url": unique_packet.url + f"/{knowinfo}",
                                            "params": unique_packet.request.params,
                                            "headers": unique_packet.request.extra_info.headers, "body": newbody}
                                response2 = {"status": 200, "body": new_response.text}
                                header = new_response.headers
                                r = self.handle_gpt(request1, response1, request2, response2,header)
                                if True == r['result']['is_vuln'] and r != {}:
                                    R.append(r)
                                    break
                            newbody[bodykey] = tmp
                        if r != {}:
                            if True == r['result']['is_vuln']:
                                break
            elif unique_packet.method == "GET" or unique_packet.method == "DELETE":
                if unique_packet.request.method == "GET":
                    method = "DELETE"
                else:
                    method = "GET"
                if unique_packet.request.params != {}:
                    for param in unique_packet.request.param:
                        for knowinfo in self.knowinfos:
                            unique_packet.request.param[param] = knowinfo
                            new_response = requests.request("GET", unique_packet.url,
                                                            params=unique_packet.request.params,
                                                            headers=unique_packet.request.extra_info.headers)
                            new_response.close()
                            if new_response.status_code == 200 and new_response.text != unique_packet.response.raw_body:
                                request1 = {"method": "GET", "url": unique_packet.url,
                                            "params": unique_packet.request.params,
                                            "headers": unique_packet.request.extra_info.headers, "body": ""}
                                response1 = {"status": 200, "body": unique_packet.response.raw_body}
                                request2 = {"method": "GET", "url": unique_packet.url,
                                            "params": unique_packet.request.params,
                                            "headers": unique_packet.request.extra_info.headers, "body": ""}
                                response2 = {"status": 200, "body": new_response.text}
                                header = new_response.headers
                                R.append(self.handle_gpt(request1, response1, request2, response2,header))
                else:
                    for knowinfo in self.knowinfos:
                        new_response = requests.request(unique_packet.method, url=unique_packet.url + "/" + knowinfo,
                                                        headers=unique_packet.request.extra_info.headers)
                        new_response.close()
                        if new_response.status_code == 200 and new_response.text != "null" and new_response.text != "":
                            request1 = {"method": unique_packet.method, "url": unique_packet.url,
                                        "params": unique_packet.request.params,
                                        "headers": unique_packet.request.extra_info.headers,
                                        "body": ""}
                            response1 = {"status": 200, "body": ""}
                            request2 = {"method": unique_packet.method,
                                        "url": unique_packet.url + f"/{knowinfo}",
                                        "params": unique_packet.request.params,
                                        "headers": unique_packet.request.extra_info.headers, "body": ""}
                            response2 = {"status": 200, "body": new_response.text}
                            header = new_response.headers
                            r = self.handle_gpt(request1, response1, request2, response2,header)
                            if True == r['result']['is_vuln'] and r != {}:
                                R.append(r)
                                break
                    for i in range(1, 20):
                        new_response = requests.request(unique_packet.method,
                                                        url=unique_packet.url + "/" + str(i),
                                                        headers=unique_packet.request.extra_info.headers)
                        new_response.close()
                        if new_response.status_code == 200 and new_response.text != "null" and new_response.text != "":
                            request1 = {"method": unique_packet.method, "url": unique_packet.url,
                                        "params": unique_packet.request.params,
                                        "headers": unique_packet.request.extra_info.headers,
                                        "body": ""}
                            response1 = {"status": 200, "body": unique_packet.response.raw_body}
                            request2 = {"method": unique_packet.method,
                                        "url": unique_packet.url + f"/{str(i)}",
                                        "params": unique_packet.request.params,
                                        "headers": unique_packet.request.extra_info.headers, "body": ""}
                            response2 = {"status": 200, "body": new_response.text}
                            header = new_response.headers
                            r = self.handle_gpt(request1, response1, request2, response2,header)
                            if True == r['result']['is_vuln'] and r != {}:
                                R.append(r)
                                break
                    for knowinfo in self.knowinfos:
                        # 解析URL并获取路径部分
                        parsed_url = urlparse(unique_packet.url)
                        path = parsed_url.path
                        scheme = parsed_url.scheme
                        net = parsed_url.netloc
                        # 按"/"分割路径，去除最后一个元素，然后重新组合
                        new_url = path.split("/")
                        new_url = new_url[:-1]  # 去除最后一个元素
                        new_url = "/".join(new_url)  # 重新组合路径
                        new_response = requests.request(unique_packet.method,
                                                        url=scheme + "://" + net + new_url + "/" + knowinfo,
                                                        headers=unique_packet.request.extra_info.headers)
                        new_response.close()
                        if new_response.status_code == 200 and new_response.text != "null" and new_response.text != "":
                            request1 = {"method": unique_packet.method, "url": unique_packet.url,
                                        "params": unique_packet.request.params,
                                        "headers": unique_packet.request.extra_info.headers,
                                        "body": ""}
                            response1 = {"status": 200, "body": unique_packet.response.raw_body}
                            request2 = {"method": unique_packet.method,
                                        "url": scheme + "://" + net + new_url + "/" + knowinfo,
                                        "params": unique_packet.request.params,
                                        "headers": unique_packet.request.extra_info.headers, "body": ""}
                            response2 = {"status": 200, "body": new_response.text}
                            header = new_response.headers
                            r = self.handle_gpt(request1, response1, request2, response2,header)
                            if True == r['result']['is_vuln']:
                                R.append(r)
                                break
                    # 解析URL并获取路径部分
                    parsed_url = urlparse(unique_packet.url)
                    path = parsed_url.path
                    scheme = parsed_url.scheme
                    net = parsed_url.netloc
                    # 按"/"分割路径，去除最后一个元素，然后重新组合
                    new_url = path.split("/")
                    new_url = new_url[:-1]  # 去除最后一个元素
                    new_url = "/".join(new_url)  # 重新组合路径
                    new_response = requests.request(unique_packet.method,
                                                    url=scheme + "://" + net + new_url + "/",
                                                    headers=unique_packet.request.extra_info.headers)
                    new_response.close()
                    if new_response.status_code == 200 and new_response.text != "null" and new_response.text != "":
                        request1 = {"method": unique_packet.method, "url": unique_packet.url,
                                    "params": unique_packet.request.params,
                                    "headers": unique_packet.request.extra_info.headers,
                                    "body": ""}
                        response1 = {"status": 200, "body": unique_packet.response.raw_body}
                        request2 = {"method": unique_packet.method,
                                    "url": scheme + "://" + net + new_url + "/",
                                    "params": unique_packet.request.params,
                                    "headers": unique_packet.request.extra_info.headers, "body": ""}
                        response2 = {"status": 200, "body": new_response.text}
                        header = new_response.headers
                        r = self.handle_gpt(request1, response1, request2, response2,header)
                        if True == r['result']['is_vuln']:
                            R.append(r)
        return R

    def handle_gpt(self, request1, response1, request2, response2,header):
        res = {}
        first_input = self.chat.handle_packet(request1, response1)
        second_input = self.chat.handle_packet(request2, response2)
        res["request"] = request2
        gpt_res = self.chat.compare_chat(first_input, second_input)
        response2.update({"headers":header})
        res["response"] = response2
        # print(gpt_res)
        json_pattern = r'\{.*?\}'
        json_str = re.search(json_pattern, gpt_res, re.DOTALL).group()
        try:
            json_str = json.loads(json_str)
        except Exception as e:
            print(e)
        res["result"] = json_str
        # make_res(str(res.json))
        # print(res.json)
        return res

    def restart_docker(self):
        # 定义docker-compose命令和参数
        down_command = ["docker-compose", "-f", "./over-permission-final/docker-compose.yml", "down"]
        # 执行命令
        subprocess.run(down_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # 定义docker-compose命令和参数
        start_command = ["docker-compose", "-f", "./over-permission-final/docker-compose.yml", "up", "-d"]
        # 执行命令
        subprocess.run(start_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(20)
        autologin = AutoLogin('http://127.0.0.1:8088', username='123', password='123456', input_text="123")
        autologin.autologin()
        autologin.test_click()
        # autologin.page.close()


