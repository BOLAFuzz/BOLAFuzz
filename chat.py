import re
import time
from typing import *

import os
import json

from openai import OpenAI
from openai.types.chat.chat_completion import Choice

from make_res import make_res


# noinspection PyTypeChecker
class ChatCompare:
    def __init__(self):
        self.client = OpenAI(
            api_key="",
            # 在这里将 MOONSHOT_API_KEY 替换为你从 Kimi 开放平台申请的 API Key
            base_url="https://api.moonshot.cn/v1",
        )
        self.packet_template = '''
        以下是request请求数据包的核心参数：
        method:{reqmethod}.url:{requrl}.cookie:{reqheader}.body:{reqbody}
        以下是response请求数据包的核心参数：
        status:{resstatus}.body:{resbody}
        '''
        self.system = "现在你是一名精通WEB-API接口越权测试的网络攻防工程师，接下来会为你提供在越权测试过程中遇到的请求和响应数据包，请你根据request数据包判断所测试的功能接口是否存在越权漏洞，并判断越权的类型是什么，对于越权的定义，只有越权到admin才是垂直越权，对于users接口的越权属于水平越权，越权到其他用户是水平越权提供的初始数据包的用户为caso4，水平越权到其他用户的名称为caso5。"
        self.messages = []
        self.info = "请根据以上数据包给出你的判断结果，以json格式返回是否存在越权漏洞is_vuln、当前功能点路由url、是何种越权reason，reason请使用固定的“水平越权”、“垂直越权”，形如{'is_vuln':True,'url':url,'reason':reason}。不需要详细进行分析，只返回结果即可，返回的结果返回传入的请求包2的路由即可，无需总结成{}的形式。"

    def search_impl(self,arguments: Dict[str, Any]) -> Any:
        """
        在使用 Moonshot AI 提供的 search 工具的场合，只需要原封不动返回 arguments 即可，
        不需要额外的处理逻辑。
        但如果你想使用其他模型，并保留联网搜索的功能，那你只需要修改这里的实现（例如调用搜索
        和获取网页内容等），函数签名不变，依然是 work 的。
        这最大程度保证了兼容性，允许你在不同的模型间切换，并且不需要对代码有破坏性的修改。
        """
        return arguments

    def make_chat(self, messages):
        completion = self.client.chat.completions.create(
            model="moonshot-v1-auto",
            messages=messages,
            temperature=0.3,
            response_format={"type": "json_object"},
            tools=[
                {
                    "type": "builtin_function",
                    "function": {
                        "name": "$web_search",
                    },
                }
            ]
        )
        usage = completion.usage
        choice = completion.choices[0]
        return choice

    def handle_packet(self, request, response):
        # packet = self.packet_template.format(reqmethod=request.method, requrl=response.url,
        #                                      reqheader=request.cookie, resstatus=response.status,
        #                                      resbody=request.body)
        packet = self.packet_template.format(reqmethod=request['method'], requrl=request['url'],
                                             reqheader=request['headers'], resstatus=response['status'],
                                             resbody=response['body'], reqbody=request['body'])

        return packet

    def compare_chat(self, first_input, second_input):
        self.messages.append({
            "role": "system",
            "content": self.system,
        })

        self.messages.append({
            "role": "user",
            "content": first_input + "\n" + second_input + self.info,
        })
        choice = self.make_chat(self.messages)
        finish_reason = choice.finish_reason
        if finish_reason == "tool_calls":  # <-- 判断当前返回内容是否包含 tool_calls
            self.messages.append(choice.message)
            for tool_call in choice.message.tool_calls:
                tool_call_name = tool_call.function.name

                tool_call_arguments = json.loads(
                    tool_call.function.arguments)  # <-- arguments 是序列化后的 JSON Object，我们需要使用 json.loads 反序列化一下
                if tool_call_name == "$web_search":
                        # ===================================================================
                        # 我们将联网搜索过程中，由联网搜索结果产生的 Tokens 打印出来
                    search_content_total_tokens = tool_call_arguments.get("usage", {}).get("total_tokens")
                    print(f"search_content_total_tokens: {search_content_total_tokens}")
                    # ===================================================================
                    tool_result = self.search_impl(tool_call_arguments)
                else:
                    tool_result = f"Error: unable to find tool by name '{tool_call_name}'"
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call_name,
                    "content": json.dumps(tool_result),
                    # <-- 我们约定使用字符串格式向 Kimi 大模型提交工具调用结果，因此在这里使用 json.dumps 将执行结果序列化成字符串
                })
        return choice.message.content