# -*- coding: utf-8 -*-
import re
import json
import random
import requests
from data_script import extract_data_from_json
from llm_script import LLMJudge
import torch
from transformers import BertTokenizer
from urllib.parse import urlparse
from faker import Faker


# Color codes
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
RESET = "\033[0m"


class Fuzz:
    def __init__(self, default_data: dict = None, test_data: dict = None):
        self.default_data = default_data if default_data is not None else {}
        self.test_data = test_data if test_data is not None else {}
        self.fk = Faker(["zh_CN", "en_US"])
        self.flag = False
        self.mutate_flag = False
        self.mark_path = None
        self.mark_path_non_intersection = {}
        self.mark_get_param = None
        self.mark_get_param_non_intersection = {}
        self.mark_post_param_data = None
        self.mark_post_param_non_intersection_data = {}
        self.mark_post_param_json = None
        self.mark_post_param_non_intersection_json = {}
        self.dict1 = ['admin', 'admin123', 'test', 'guest', 'user', 'root', 'administrator', 'webadmin', 'sysadmin', 'superadmin', 'test1', 'test2', '0', '1', '01']
        self.model = torch.load('model_full.pth', weights_only=False, map_location=torch.device('cpu'))
        self.model.eval()

    def start(self):
        pass

    def mark_non_intersection(self):
        self.path_non_intersection()
        self.param_non_intersection()
        self.body_non_intersection()
        self.auto_mutate()

    def path_non_intersection(self):
        # 分割路径部分
        parsed_url1 = urlparse(self.default_data['Url'][:-1] if self.default_data['Url'].endswith('/') else self.default_data['Url'])
        parsed_url2 = urlparse(self.test_data['Url'][:-1] if self.test_data['Url'].endswith('/') else self.test_data['Url'])
        path1_parts = parsed_url1.path.split('/')
        path2_parts = parsed_url2.path.split('/')

        # 寻找最长公共前缀
        common_prefix = []
        for part1, part2 in zip(path1_parts, path2_parts):
            if part1 == part2:
                common_prefix.append(part1)
            else:
                break

        # 初始化标记记录字典, 生成标记后的URL和差异部分
        mark_dict = {}
        mark_counter = 1

        marked_url = f"{parsed_url1.scheme}://{parsed_url1.netloc}"
        for i in range(len(common_prefix)):
            if i != 0:
                marked_url += f"/{common_prefix[i]}"
            else:
                marked_url += f"{common_prefix[i]}"

        for i in range(len(common_prefix), max(len(path1_parts), len(path2_parts))):
            if i < len(path1_parts) and i < len(path2_parts):
                if path1_parts[i] != path2_parts[i]:
                    mark = f"mark{mark_counter}"
                    marked_url += f"/{mark}"
                    mark_dict[mark] = (path1_parts[i], path2_parts[i])
                    mark_counter += 1
                else:
                    marked_url += f"/{path1_parts[i]}"
            elif i < len(path1_parts):
                mark = f"mark{mark_counter}"
                marked_url += f"/{mark}"
                mark_dict[mark] = (path1_parts[i], "")
                mark_counter += 1
            elif i < len(path2_parts):
                mark = f"mark{mark_counter}"
                marked_url += f"/{mark}"
                mark_dict[mark] = ("", path2_parts[i])
                mark_counter += 1

        self.mark_path = marked_url
        self.mark_path_non_intersection = mark_dict


    def param_non_intersection(self):
        if len(self.default_data['Params']) == 1 and self.default_data['Params'][0] == '':
            return
        # 初始化标记记录字典和标记后的参数列表
        mark_dict = {}
        marked_params = []
        mark_counter = 1

        params1 = {}
        for param in self.default_data['Params']:
            key, value = param.split('=')
            params1[key] = value
        params2 = {}
        for param in self.test_data['Params']:
            key, value = param.split('=')
            params2[key] = value   
        
        # 比较两个字典
        all_keys = set(params1.keys()).union(set(params2.keys()))
        for key in all_keys:
            if key not in params1 or key not in params2:
                # 如果某个键只存在于一个字典中
                if key in params1:
                    mark = f"param_mark{mark_counter}"
                    mark_dict[mark] = (params1[key], "")
                    marked_params.append(f"{key}={mark}")
                else:
                    mark = f"param_mark{mark_counter}"
                    mark_dict[mark] = ("", params2[key])
                    marked_params.append(f"{key}={mark}")
                mark_counter += 1
            elif params1[key] != params2[key]:
                # 如果键存在但值不同
                mark = f"param_mark{mark_counter}"
                mark_dict[mark] = (params1[key], params2[key])
                marked_params.append(f"{key}={mark}")
                mark_counter += 1
            else:
                # 如果键和值都相同
                marked_params.append(f"{key}={params1[key]}")

        # 生成标记后的查询参数字符串
        self.mark_get_param = '&'.join(marked_params)
        self.mark_get_param_non_intersection = mark_dict

    def parse_form_data(self, body):
        params_dict = {}
        for param in body.split('&'):
            key, value = param.split('=')
            params_dict[key] = value
        return params_dict

    def body_non_intersection_data(self, body1, body2):
        params_dict1 = self.parse_form_data(body1)
        params_dict2 = self.parse_form_data(body2)
        
        mark_dict = {}
        marked_params = []
        mark_counter = 1
        
        all_keys = set(params_dict1.keys()).union(set(params_dict2.keys()))
        for key in all_keys:
            if key not in params_dict1 or key not in params_dict2:
                if key in params_dict1:
                    mark = f"body_mark{mark_counter}"
                    mark_dict[mark] = (params_dict1[key], "")
                    marked_params.append(f"{key}={mark}")
                else:
                    mark = f"body_mark{mark_counter}"
                    mark_dict[mark] = ("", params_dict2[key])
                    marked_params.append(f"{key}={mark}")
                mark_counter += 1
            elif params_dict1[key] != params_dict2[key]:
                mark = f"body_mark{mark_counter}"
                mark_dict[mark] = (params_dict1[key], params_dict2[key])
                marked_params.append(f"{key}={mark}")
                mark_counter += 1
            else:
                marked_params.append(f"{key}={params_dict1[key]}")
        
        marked_body = '&'.join(marked_params)
        self.mark_post_param_data = marked_body
        self.mark_post_param_non_intersection_data = mark_dict

    def body_non_intersection_json(self, body1, body2):
        json1 = json.loads(body1)
        json2 = json.loads(body2)
        
        mark_dict = {}
        marked_json = {}
        mark_counter = 1
        
        def compare_and_mark_recursive(obj1, obj2, path=""):
            nonlocal mark_counter
            for key in set(obj1.keys()).union(set(obj2.keys())):
                if key not in obj1 or key not in obj2:
                    if key in obj1:
                        mark = f"body_mark{mark_counter}"
                        mark_dict[mark] = (obj1[key], "")
                        marked_json[key] = mark
                    else:
                        mark = f"body_mark{mark_counter}"
                        mark_dict[mark] = ("", obj2[key])
                        marked_json[key] = mark
                    mark_counter += 1
                elif obj1[key] != obj2[key]:
                    if isinstance(obj1[key], dict) and isinstance(obj2[key], dict):
                        marked_json[key] = {}
                        compare_and_mark_recursive(obj1[key], obj2[key], path + key + ".")
                    else:
                        mark = f"body_mark{mark_counter}"
                        mark_dict[mark] = (obj1[key], obj2[key])
                        marked_json[key] = mark
                        mark_counter += 1
                else:
                    marked_json[key] = obj1[key]
        
        compare_and_mark_recursive(json1, json2)
        
        marked_body = json.dumps(marked_json, indent=2)
        self.mark_post_param_json = marked_body
        self.mark_post_param_non_intersection_json = mark_dict

    def body_non_intersection(self):
        json_pattern = re.compile(r'^\s*\{.*\}\s*$')
        form_data_pattern = re.compile(r'^[a-zA-Z0-9_\-]+=[^&]+(&[a-zA-Z0-9_\-]+=[^&]+)*$')
        
        body1 = self.default_data['Body']
        body2 = self.test_data['Body']
        if json_pattern.match(body1) and json_pattern.match(body2):
            return self.body_non_intersection_json(body1, body2)
        elif form_data_pattern.match(body1) and form_data_pattern.match(body2):
            return self.body_non_intersection_data(body1, body2)
        else:
            # print(f"{RED}[x] Unsupported body format...{RESET}")
            return

    def auto_identify(self, data):
        """自动识别标记参数类型"""
        tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        input_tensor= tokenizer(str(data), return_tensors="pt")

        with torch.no_grad():
            output = self.model(**input_tensor)
            logits = output.logits

        predicted_label = str(torch.argmax(logits, dim=1).item())
        print(f"data: {data}, predicted label: {predicted_label}")

        return predicted_label

    def auto_mutate(self):
        """自动识别标记参数类型"""
        # 先进行路径变异
        if len(self.mark_path_non_intersection) >= 1 and 'mark' in self.mark_path:
            if len(self.mark_path_non_intersection) == 1:
                default_label = self.auto_identify(self.mark_path_non_intersection['mark1'][0])
                self.mutate(default_label, self.mark_path_non_intersection['mark1'][0], self.mark_path_non_intersection['mark1'][1], 'mark1')
            elif len(self.mark_path_non_intersection) > 1:
                for i in range(len(self.mark_path_non_intersection)):
                    tmp = 'mark' + str(i+1)
                    default_label = self.auto_identify(self.mark_path_non_intersection[tmp][0])
                    self.mutate(default_label, self.mark_path_non_intersection[tmp][0], self.mark_path_non_intersection[tmp][1], tmp)

        # 接着进行参数变异
        if len(self.mark_get_param_non_intersection) >= 1 and 'param_mark' in self.mark_get_param:
            if len(self.mark_get_param_non_intersection) == 1:
                default_label = self.auto_identify(self.mark_get_param_non_intersection['param_mark1'][0])
                self.mutate(default_label, self.mark_get_param_non_intersection['param_mark1'][0], self.mark_get_param_non_intersection['param_mark1'][1], 'param_mark1')
            elif len(self.mark_get_param_non_intersection) > 1:
                for i in range(len(self.mark_get_param_non_intersection)):
                    tmp = 'param_mark' + str(i+1)
                    default_label = self.auto_identify(self.mark_get_param_non_intersection[tmp][0])
                    self.mutate(default_label, self.mark_get_param_non_intersection[tmp][0], self.mark_get_param_non_intersection[tmp][1], tmp)

        # 接着进行Body变异
        if len(self.mark_post_param_non_intersection_data) >= 1 and 'body_mark' in self.mark_post_param_data:
            if len(self.mark_post_param_non_intersection_data) == 1:
                default_label = self.auto_identify(self.mark_post_param_non_intersection_data['body_mark1'][0])
                self.mutate(default_label, self.mark_post_param_non_intersection_data['body_mark1'][0], self.mark_post_param_non_intersection_data['body_mark1'][1], 'body_mark1')
            elif len(self.mark_post_param_non_intersection_data) > 1:
                for i in range(len(self.mark_post_param_non_intersection_data)):
                    tmp = 'body_mark' + str(i+1)
                    default_label = self.auto_identify(self.mark_post_param_non_intersection_data[tmp][0])
                    self.mutate(default_label, self.mark_post_param_non_intersection_data[tmp][0], self.mark_post_param_non_intersection_data[tmp][1], tmp)
        elif len(self.mark_post_param_non_intersection_json) >= 1 and 'body_mark' in self.mark_post_param_json:
            if len(self.mark_post_param_non_intersection_json) == 1:
                default_label = self.auto_identify(self.mark_post_param_non_intersection_json['body_mark1'][0])
                self.mutate(default_label, self.mark_post_param_non_intersection_json['body_mark1'][0], self.mark_post_param_non_intersection_json['body_mark1'][1], 'body_mark1')
            elif len(self.mark_post_param_non_intersection_json) > 1:
                for i in range(len(self.mark_post_param_non_intersection_json)):
                    tmp = 'body_mark' + str(i+1)
                    default_label = self.auto_identify(self.mark_post_param_non_intersection_json[tmp][0])
                    self.mutate(default_label, self.mark_post_param_non_intersection_json[tmp][0], self.mark_post_param_non_intersection_json[tmp][1], tmp)

    def mutate(self, label, self_data, data, mark):
        """变异模块"""
        if label == '0' or label == '1' or label == '3' or label == '7' or label == '8':
            if self.flag == False and data != '':
                self.process_req_data(data, mark)
        elif label == '2':
            if self.mutate_flag == False and self.flag == False and data != '':
                self.mutate_flag = True
                self.process_req_data(data, mark)
            elif self.mutate_flag and self.flag == False:
                for data in self.dict1:
                    self.process_req_data(data, mark)
        elif label == '4':
            if self.mutate_flag == False and self.flag == False and data != '':
                self.mutate_flag = True
                self.process_req_data(data, mark)
            elif self.mutate_flag and self.flag == False:
                for _ in range(10):
                    prefix = (self_data[:3] if self_data else data[:3])
                    suffix = ''.join(str(random.randint(0, 9)) for _ in range(len(self_data if self_data else data) - 3))
                    self.process_req_data(prefix + suffix, mark)
        elif label == '5':
            if self.mutate_flag == False and self.flag == False and data != '':
                self.mutate_flag = True
                self.process_req_data(data, mark)
            elif self.mutate_flag and self.flag == False:
                for _ in range(10):
                    self.process_req_data(self.fk.ssn(), mark)
        elif label == '6':
            if self.mutate_flag == False and self.flag == False and data != '':
                self.mutate_flag = True
                self.process_req_data(data, mark)
            elif self.mutate_flag and self.flag == False:
                for data in self.dict1:
                    _, domain = data.split('@')
                    self.process_req_data(f"{data}@{domain}", mark)
        elif label == '9':
            if self.mutate_flag == False and self.flag == False and data != '':
                self.mutate_flag = True
                self.process_req_data(data, mark)
            elif self.mutate_flag and self.flag == False:
                for _ in range(5):
                    self.process_req_data(int(self_data if self_data else data) + random.randint(-100, 100), mark)
                for i in range(15):
                    self.process_req_data(int(self_data if self_data else data) + i, mark)
        elif label == '10':
            if self.mutate_flag == False and self.flag == False and data != '':
                self.mutate_flag = True
                self.process_req_data(data, mark)
            elif self.mutate_flag and self.flag == False:
                for _ in range(10):
                    max_change = 10
                    parts = re.split(r'(\d+)', (self_data if self_data else data))
                    for i in range(len(parts)):
                        if parts[i].isdigit():
                            num = int(parts[i])
                            original_length = len(parts[i])
                            change = random.randint(-max_change, max_change)
                            new_num = max(0, num + change)
                            parts[i] = new_num
                            # parts[i] = f"{new_num:0{original_length}d}"
                    self.process_req_data(''.join(parts), mark)


    def process_req_data(self, fuzz_data, mark):
        # TODO: 需要注意类型转换，变异后的结果需要注意原数据类型是INT还是String
        if 'param_mark' in mark:
            if len(self.mark_get_param_non_intersection) == 1:
                url = self.default_data['Url']
                params = self.mark_get_param.replace(mark, str(fuzz_data))
                if self.default_data['Method'] == 'GET':
                    resp = requests.get(
                        url=url,
                        headers=self.default_data['Headers'],
                        params=dict(item.split('=') for item in params.split('&')),
                    )
                    request_data = {
                        "request": {
                            "url": url,
                            "method": "GET",
                            "headers": self.default_data['Headers'],
                            "Params": dict(item.split('=') for item in params.split('&')),
                            "body": ""
                        }
                    }
                    response_data = {
                        "response": {
                            "url": url,
                            "headers": dict(resp.headers),
                            "body": resp.text
                        }
                    }
                    self.llm_judge(request_data, response_data, str(fuzz_data))
                elif self.default_data['Method'] == 'POST':
                    tmp_data = self.default_data['Body']
                    if re.match(r'^\{.*\}$', self.default_data['Body']):
                        resp = requests.post(
                            url=url,
                            headers=self.default_data['Headers'],
                            params=dict(item.split('=') for item in params.split('&')),
                            json=json.loads(self.default_data['Body']),
                        )
                        tmp_data = json.loads(self.default_data['Body'])
                    else:
                        resp = requests.post(
                            url=url,
                            headers=self.default_data['Headers'],
                            params=dict(item.split('=') for item in params.split('&')),
                            data=self.default_data['Body'],
                        )
                    request_data = {
                        "request": {
                            "url": url,
                            "method": "POST",
                            "headers": self.default_data['Headers'],
                            "Params": dict(item.split('=') for item in params.split('&')),
                            "body": tmp_data
                        }
                    }
                    response_data = {
                        "response": {
                            "url": url,
                            "headers": dict(resp.headers),
                            "body": resp.text
                        }
                    }
                    self.llm_judge(request_data, response_data, str(fuzz_data))
            elif len(self.mark_get_param_non_intersection) > 1:
                url = self.default_data['Url']
                params = self.mark_get_param.replace(mark, str(fuzz_data))
                for m, v in self.mark_get_param_non_intersection.items():
                    params = params.replace(m, str(v[0]))
                if self.default_data['Method'] == 'GET':
                    resp = requests.get(
                        url=url,
                        headers=self.default_data['Headers'],
                        params=dict(item.split('=') for item in params.split('&')),
                    )
                    request_data = {
                        "request": {
                            "url": url,
                            "method": "GET",
                            "headers": self.default_data['Headers'],
                            "Params": dict(item.split('=') for item in params.split('&')),
                            "body": ""
                        }
                    }
                    response_data = {
                        "response": {
                            "url": url,
                            "headers": dict(resp.headers),
                            "body": resp.text
                        }
                    }
                    self.llm_judge(request_data, response_data, str(fuzz_data))
                elif self.default_data['Method'] == 'POST':
                    tmp_data = self.default_data['Body']
                    if re.match(r'^\{.*\}$', self.default_data['Body']):
                        resp = requests.post(
                            url=url,
                            headers=self.default_data['Headers'],
                            params=dict(item.split('=') for item in params.split('&')),
                            json=json.loads(self.default_data['Body']),
                        )
                        tmp_data = json.loads(self.default_data['Body'])
                    else:
                        resp = requests.post(
                            url=url,
                            headers=self.default_data['Headers'],
                            params=dict(item.split('=') for item in params.split('&')),
                            data=self.default_data['Body'],
                        )
                    request_data = {
                        "request": {
                            "url": url,
                            "method": "POST",
                            "headers": self.default_data['Headers'],
                            "Params": dict(item.split('=') for item in params.split('&')),
                            "body": tmp_data
                        }
                    }
                    response_data = {
                        "response": {
                            "url": url,
                            "headers": dict(resp.headers),
                            "body": resp.text
                        }
                    }
                    self.llm_judge(request_data, response_data, str(fuzz_data))
        elif 'body_mark' in mark:
            if len(self.mark_post_param_non_intersection_data) == 1 or len(self.mark_post_param_non_intersection_json) == 1:
                url = self.default_data['Url']
                params = self.default_data['Params']
                data = self.default_data['Body'].replace(mark, str(fuzz_data))
                if self.default_data['Method'] == 'POST':
                    tmp_data = data
                    if re.match(r'^\{.*\}$', self.default_data['Body']):
                        resp = requests.post(
                            url=url,
                            headers=self.default_data['Headers'],
                            params={param.split('=')[0]: param.split('=')[1] for param in params if param.split('=') != ['']},
                            json=json.loads(data),
                        )
                        tmp_data = json.loads(data)
                    else:
                        resp = requests.post(
                            url=url,
                            headers=self.default_data['Headers'],
                            params={param.split('=')[0]: param.split('=')[1] for param in params if param.split('=') != ['']},
                            data=data,
                        )
                    request_data = {
                        "request": {
                            "url": url,
                            "method": "POST",
                            "headers": self.default_data['Headers'],
                            "Params": {param.split('=')[0]: param.split('=')[1] for param in params if param.split('=') != ['']},
                            "body": tmp_data
                        }
                    }
                    response_data = {
                        "response": {
                            "url": url,
                            "headers": dict(resp.headers),
                            "body": resp.text
                        }
                    }
                    self.llm_judge(request_data, response_data, str(fuzz_data))
            elif len(self.mark_post_param_non_intersection_data) > 1 or len(self.mark_post_param_non_intersection_json) > 1:
                url = self.default_data['Url']
                params = self.default_data['Params']
                data = self.default_data['Body'].replace(mark, str(fuzz_data))
                if len(self.mark_post_param_non_intersection_data) > 1:
                    for m, v in self.mark_post_param_non_intersection_data.items():
                        data = data.replace(m, str(v[0]))
                elif len(self.mark_post_param_non_intersection_json) > 1:
                    for m, v in self.mark_post_param_non_intersection_json.items():
                        data = data.replace(m, str(v[0]))
                if self.default_data['Method'] == 'POST':
                    tmp_data = data
                    if re.match(r'^\{.*\}$', self.default_data['Body']):
                        resp = requests.post(
                            url=url,
                            headers=self.default_data['Headers'],
                            params={param.split('=')[0]: param.split('=')[1] for param in params if param.split('=') != ['']},
                            json=json.loads(data),
                        )
                        tmp_data = json.loads(data)
                    else:
                        resp = requests.post(
                            url=url,
                            headers=self.default_data['Headers'],
                            params={param.split('=')[0]: param.split('=')[1] for param in params if param.split('=') != ['']},
                            data=data,
                        )
                    request_data = {
                        "request": {
                            "url": url,
                            "method": "POST",
                            "headers": self.default_data['Headers'],
                            "Params": {param.split('=')[0]: param.split('=')[1] for param in params if param.split('=') != ['']},
                            "body": tmp_data
                        }
                    }
                    response_data = {
                        "response": {
                            "url": url,
                            "headers": dict(resp.headers),
                            "body": resp.text
                        }
                    }
                    self.llm_judge(request_data, response_data, str(fuzz_data))
        elif 'mark' in mark:
            if len(self.mark_path_non_intersection) == 1:
                url = self.mark_path.replace(mark, str(fuzz_data))
                if self.default_data['Method'] == 'GET':
                    resp = requests.get(
                        url=url,
                        headers=self.default_data['Headers'],
                        params={param.split('=')[0]: param.split('=')[1] for param in self.default_data['Params'] if param.split('=') != ['']},
                    )
                    request_data = {
                        "request": {
                            "url": url,
                            "method": "GET",
                            "headers": self.default_data['Headers'],
                            "Params": {param.split('=')[0]: param.split('=')[1] for param in self.default_data['Params'] if param.split('=') != ['']},
                            "body": self.default_data['Body']
                        }
                    }
                    response_data = {
                        "response": {
                            "url": url,
                            "headers": dict(resp.headers),
                            "body": resp.text
                        }
                    }
                    self.llm_judge(request_data, response_data, str(fuzz_data))
                elif self.default_data['Method'] == 'POST':
                    tmp_data = data
                    if re.match(r'^\{.*\}$', self.default_data['Body']):
                        resp = requests.post(
                            url=url,
                            headers=self.default_data['Headers'],
                            params={param.split('=')[0]: param.split('=')[1] for param in self.default_data['Params'] if param.split('=') != ['']},
                            json=json.loads(self.default_data['Body']),
                        )
                        tmp_data = json.loads(self.default_data['Body'])
                    else:
                        resp = requests.post(
                            url=url,
                            headers=self.default_data['Headers'],
                            params={param.split('=')[0]: param.split('=')[1] for param in self.default_data['Params'] if param.split('=') != ['']},
                            data=self.default_data['Body'],
                        )
                    request_data = {
                        "request": {
                            "url": url,
                            "method": "POST",
                            "headers": self.default_data['Headers'],
                            "Params": {param.split('=')[0]: param.split('=')[1] for param in self.default_data['Params'] if param.split('=') != ['']},
                            "body": tmp_data
                        }
                    }
                    response_data = {
                        "response": {
                            "url": url,
                            "headers": dict(resp.headers),
                            "body": resp.text
                        }
                    }
                    self.llm_judge(request_data, response_data, str(fuzz_data))
            elif len(self.mark_path_non_intersection) > 1:
                url = self.mark_path.replace(mark, str(fuzz_data))
                for m, v in self.mark_path_non_intersection.items():
                    url = url.replace(m, str(v[0]))
                if self.default_data['Method'] == 'GET':
                    resp = requests.get(
                        url=url,
                        headers=self.default_data['Headers'],
                        params={param.split('=')[0]: param.split('=')[1] for param in self.default_data['Params'] if param.split('=') != ['']},
                    )
                    request_data = {
                        "request": {
                            "url": url,
                            "method": "GET",
                            "headers": self.default_data['Headers'],
                            "Params": {param.split('=')[0]: param.split('=')[1] for param in self.default_data['Params'] if param.split('=') != ['']},
                            "body": self.default_data['Body']
                        }
                    }
                    response_data = {
                        "response": {
                            "url": url,
                            "headers": dict(resp.headers),
                            "body": resp.text
                        }
                    }
                    self.llm_judge(request_data, response_data, str(fuzz_data))
                elif self.default_data['Method'] == 'POST':
                    tmp_data = self.default_data['Body']
                    if re.match(r'^\{.*\}$', self.default_data['Body']):
                        resp = requests.post(
                            url=url,
                            headers=self.default_data['Headers'],
                            params={param.split('=')[0]: param.split('=')[1] for param in self.default_data['Params'] if param.split('=') != ['']},
                            json=json.loads(self.default_data['Body']),
                        )
                        tmp_data = json.loads(self.default_data['Body'])
                    else:
                        resp = requests.post(
                            url=url,
                            headers=self.default_data['Headers'],
                            params={param.split('=')[0]: param.split('=')[1] for param in self.default_data['Params'] if param.split('=') != ['']},
                            data=self.default_data['Body'],
                        )
                    request_data = {
                        "request": {
                            "url": url,
                            "method": "POST",
                            "headers": self.default_data['Headers'],
                            "Params": {param.split('=')[0]: param.split('=')[1] for param in self.default_data['Params'] if param.split('=') != ['']},
                            "body": tmp_data
                        }
                    }
                    response_data = {
                        "response": {
                            "url": url,
                            "headers": dict(resp.headers),
                            "body": resp.text
                        }
                    }
                    self.llm_judge(request_data, response_data, str(fuzz_data))


    def llm_judge(self, compare_request_data, compare_response_data, fuzz_data):
        """请求目标网站获取请求响应数据包"""
        default_request_data = {
            "request": {
                "url": self.default_data['Url'],
                "method": "POST",
                "headers": self.default_data['Headers'],
                "Params": {param.split('=')[0]: param.split('=')[1] for param in self.default_data['Params'] if param.split('=') != ['']},
                "body": self.default_data['Body']
            }
        }
        default_response_data = {'response': self.default_data['Response']}
        judge_result = LLMJudge(fuzz=fuzz_data, req1=default_request_data, resp1=default_response_data, req2=compare_request_data, resp2=compare_response_data)
        print(judge_result.llm_run())



def extract_path_nodes(url):
    path = url.split('//')[-1].split('/', 1)[-1]
    nodes = path.split('/')
    nodes = [node for node in nodes if node]
    return nodes

def lcs_length(X, Y):
    m = len(X)
    n = len(Y)
    L = [[0] * (n + 1) for i in range(m + 1)]
    
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 or j == 0:
                L[i][j] = 0
            elif X[i - 1] == Y[j - 1]:
                L[i][j] = L[i - 1][j - 1] + 1
            else:
                L[i][j] = max(L[i - 1][j], L[i][j - 1])
    
    return L[m][n]

def compare_urls(url1, url2):
    nodes1 = extract_path_nodes(url1)
    nodes2 = extract_path_nodes(url2)
    
    lcs_len = lcs_length(nodes1, nodes2)
    max_len = max(len(nodes1), len(nodes2))
    
    similarity = lcs_len / max_len if max_len > 0 else 0
    return similarity

def lcs_compare(label, labels):
    most_similar_url = None
    max_similarity = 0

    for url in labels:
        similarity = compare_urls(label, url)
        if similarity > max_similarity:
            max_similarity = similarity
            most_similar_url = url

    return most_similar_url
    # print(f"{BLUE}[>] the most similar URL is: {most_similar_url}, the similarity is: {max_similarity:.2%}{RESET}")

def process_requests(datas):
    # 获取所有用户列表
    users = list(datas.keys())
    # 判断用户数量
    if len(users) <= 1:
        raise ValueError(f"{RED}[x] There must be more than one user to proceed...{RESET}")
    
    # 默认用户为首用户
    default_user = users[0]
    default_user_data = datas[default_user]
    default_user_label = {data["Label"]: data for data in default_user_data}

    # 随机挑选另一个用户
    test_user = random.choice(users[1:])
    test_user_data = datas[test_user]
    test_user_label = {data["Label"]: data for data in test_user_data}

    # 按照默认用户的请求数据顺序进行操作
    for label in default_user_label:
        print(f"{BLUE}[>] fuzzing url start: {label}{RESET}")
        # Find a matching UrlLabel in the request data of another user
        compare_label = lcs_compare(label=label, labels=list(test_user_label.keys()))
        if compare_label is not None:
            fuzz_driver = Fuzz(default_data=default_user_label[label], test_data=test_user_label[compare_label])
            fuzz_driver.mark_non_intersection()
        else:
            print(f"{CYAN}[>] fuzzing url end: {label}{RESET}")


def process_website(extracted_data):
    print(f"{GREEN}[>] loading fuzzy module...{RESET}")
    for i in range(0, len(extracted_data)):
        process_requests(datas=extracted_data[i])
        # exit()


extracted_data = extract_data_from_json(file_path="output.json")
process_website(extracted_data=extracted_data)

