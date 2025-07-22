# -*- coding: utf-8 -*-
import json
import warnings
import requests
from openai import OpenAI
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_ollama import ChatOllama
warnings.filterwarnings("ignore")

# LLM_MODEL = ChatOllama(model="qwen2:7b", max_tokens=2048, temperature=0)

# SYSTEM_TEMPLATE = r"""
# - Role: Web Security Researcher and Vulnerability Analyst
# - Background: The user is an expert in web application security research and needs to identify Broken Access Control vulnerabilities by analyzing HTTP request and response pairs. The requests include fuzzed parameters, and the goal is to determine if the responses indicate a vulnerability.
# - Profile: As a Web Security Researcher, you possess a deep understanding of web application security principles, including the OWASP Top 10 vulnerabilities. You are skilled in analyzing HTTP traffic and have experience with fuzzing techniques to test for security flaws.
# - Skills: You have the ability to dissect HTTP requests and responses, identify anomalies in response codes and body content, and correlate these with potential security vulnerabilities such as Broken Access Control.
# - Goals: To accurately determine the presence of Broken Access Control vulnerabilities by comparing the responses to fuzzed requests against expected outcomes.
# - Constrains: The analysis must be based solely on the provided HTTP request and response data without making additional requests or relying on external tools.
# - OutputFormat: A boolean value (TRUE or FALSE) indicating the presence or absence of a Broken Access Control vulnerability.
# - Workflow:
#   1. Parse the provided HTTP request and response pairs.
#   2. Identify and compare the status codes and body content of the responses.
#   3. Evaluate if the differences in responses suggest unauthorized access or data exposure, indicative of a Broken Access Control vulnerability.
#   4. Return TRUE if a vulnerability is detected, otherwise return FALSE.
# """
# # \"\"\"
# PROMPT_TEMPLATE = '''
# Request-Response Pair 1:
# Request:
# """
# {req1}
# """
# Response:
# """
# {resp1}
# """

# Request-Response Pair 2 (fuzzed parameter value is {fuzz}):
# Request:
# """
# {req2}
# """
# Response:
# """
# {resp2}
# """

# Please follow the guidelines to determine the presence of Broken Access Control vulnerabilities.
# Just return "TRUE" if a vulnerability is detected, otherwise return "FALSE".
# '''


# url = 'http://localhost:11434/api/chat'
# data = {
#     "model": "qwen2:7b",
#     "stream": False,
#     "messages": [
#         {
#             "role": "system",
#             "content": SYSTEM_TEMPLATE
#         },
#         {
#             "role": "user",
#             "content": PROMPT_TEMPLATE.format(fuzz=fuzz, req1=req1, resp1=resp1, req2=req2, resp2=resp2)
#         }
#     ]
# }

# headers = {'Content-Type': 'application/json'}
# response = requests.post(url, data=json.dumps(data), headers=headers)
# print(response.text)


class LLMJudge():
    def __init__(self, fuzz: str, req1: dict = None, resp1: dict = None, req2: dict = None, resp2: dict = None):
        self.default_request_data = req1 if req1 is not None else {}
        self.default_response_data = resp1 if resp1 is not None else {}
        self.compare_request_data = req2 if req2 is not None else {}
        self.compare_response_data = resp2 if resp2 is not None else {}
        self.CLIENT = OpenAI(
            api_key="sk-85050fde7e9e45ddbd172f2807a2068a", 
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.SYSTEM_TEMPLATE = """
            **角色描述**：你是一个判断是否存在越权的分析机器人，通过对比两个HTTP请求与响应数据包的相似性，判断是否存在越权漏洞，并根据要求给出判断结果
            **输入介绍**：用户提供了两个响应内容：
            - **请求A**：正常请求资源接口的请求
            - **响应A**：正常请求资源接口的响应
            - **请求B**：利用模糊测试技术修改了部分URL参数或请求体参数后请求资源接口的请求
            - **响应B**：利用模糊测试技术修改了部分URL参数或请求体参数后请求资源接口的响应

            **分析要求**：
            1. **对比响应内容**：
                - 忽略动态字段（如时间戳、traceID、会话ID等每次请求可能变化的字段）
                - 重点对比响应A和B的**非动态字段的结构和内容差异**

            2. **判断依据**：
                - **越权成功（true）**：
                - 若响应A和B的非动态字段结构完全一致，且A中有值的字段在B中有值或为null(因为b可能确实没数据，不代表越权失败)，内容不同但符合同类型数据规则，皆判定为越权成功，返回true
                - 若响应B包含响应A中业务数据对应的字段结构，但字段内容变为与他人资源有关（如他人资源的ID、名称等）的值或字段内容值为null(因为b可能确实没数据，不代表越权失败)，皆判定为越权成功，返回true
                - 若响应A和B中都存在`success`字段且值为`true`，结构一致且响应内容较短无公开接口信息，则可能为操作接口成功，判定越权成功，返回true
                - **越权失败（false）**：
                - 若响应B明确返回错误信息（如“权限不足”、“资源不可访问”或HTTP状态码403/401等），判定为越权失败，返回false
                - 若响应A和B的非动态字段结构、字段值完全一致，判定越权失败
                - 若响应A和B的字段结构显著不同（如字段数量、层级、命名等差异），尤其是B的内容与A的响应中的类型明显不相关，判定为越权失败，返回false
                - 若响应B包含字段跟响应A中的业务字段完全无关，判定为越权失败，返回false
                - **其他情况（unknown）**：
                - 若响应B包含与资源A无关的业务数据字段和值，无法明确判断是否越权，返回unknown
                - 若响应A和B的差异难以判断是否符合越权条件，返回未知unknown

            3. **输出格式**：
                - 返回JSON格式的结果：`res`字段值为字符串格式，只能是`'true'`、`'false'`或`'unknown'`。
                - 示例：`{"res":"true", "reason":"不超过50字的判断原因"}`
                - `reason`字段说明判断原因，注意不能超过50字

            **注意事项**：
            1. 仅输出JSON格式的结果，不添加任何额外文本或解释
            2. 确保JSON格式正确，以便于后续处理
            3. 保持客观中立，仅根据提供的响应内容进行分析

            **总体流程**：
            1. 接收并理解请求和响应A、请求和响应B
            2. 忽略动态字段，重点对比非动态字段的结构和内容差异
            3. 逐步进行分析，严格按照前面的判断依据得出结论并输出指定JSON格式的结果
        """
        self.PROMPT_TEMPLATE = '''
            fuzzed parameter value: {fuzz}
            Request A: {req1}
            Response A: {resp1}

            Request B: {req2}
            Response B: {resp2}
            '''.format(fuzz=fuzz, req1=self.default_request_data, resp1=self.default_response_data, req2=self.compare_request_data, resp2=self.compare_response_data)

    def llm_run(self):
        # LLM_MODEL = ChatOllama(model="qwen2:7b", max_tokens=8192, temperature=0)
        # data = {
        #     "model": "qwen2:7b",
        #     "stream": False,
        #     "messages": [
        #         {
        #             "role": "system",
        #             "content": self.SYSTEM_TEMPLATE
        #         },
        #         {
        #             "role": "user",
        #             "content": self.PROMPT_TEMPLATE
        #         }
        #     ]
        # }

        # response = LLM_MODEL.invoke(data["messages"], stream=False)
        # return response.content

        
        completion = self.CLIENT.chat.completions.create(
            model = "qwen-plus", # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
            messages=[
            {'role': 'system', 'content': self.SYSTEM_TEMPLATE},
            {'role': 'user', 'content': self.PROMPT_TEMPLATE}],
        )
        print(completion.model_dump_json())