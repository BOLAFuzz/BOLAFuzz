import pickle



def make_html():
        # 打开一个文件用于读取
    with open('my_list.pkl', 'rb') as file:
        # 使用load()函数从文件中读取序列化后的数据，并将其还原为原始的Python对象
        my_list = pickle.load(file)

    for packet in my_list:
        tmp_header = "\n".join(f"{key}: {value}" for key, value in packet['request']["headers"].items())
        param = ""
        try:
            if packet['request']["params"] != {}:
                for key, value in packet['request']["params"].items():
                    tmp_param = "".join(f"{key}={value}")+"&"
                    param += tmp_param
                param = "?"+param[:-1]
        except:
            param = ""
        if packet['request']["method"] == "GET":
            request_section_get = f'''{packet['request']["method"]} {packet['request']["url"]}{param} HTTP/1.1
{tmp_header}
            '''
            packet["request"] = request_section_get
        else:
            request_section_post = f'''{packet['request']["method"]} {packet['request']["url"]}{param} HTTP/1.1
{tmp_header}

{packet['request']["body"]}
            '''
            packet["request"] = request_section_post

    for packet in my_list:
        # 创建一个空列表来存储头部信息
        headers_list = []
        # 遍历 packet['request']["headers"] 字典中的每个键值对
        for key, value in packet['response']["headers"].items():
            # 检查键名是否为 'Date'（不区分大小写）
            if key.lower() != 'date':
                # 如果不是 'Date'，则将该键值对添加到列表中
                headers_list.append(f"{key}: {value}")

        # 使用 '\n' 将列表中的所有字符串连接起来
        tmp_header = "\n".join(headers_list)
        response_section_post = f'''HTTP/1.1 {packet['response']["status"]} OK
{tmp_header}

{packet['response']["body"]}
            '''
        packet["response"] = response_section_post


    # HTML模板
    template = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>Web应用越权漏洞扫描结果</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f4f4f4;
                text-align: center;
            }
            .container {
                width: 90%;
                margin: auto;
                background-color: #fff;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                text-align: left;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
                margin-bottom: 15px;
                table-layout: auto;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
            }
            th {
                background-color: #2864dd;
                color: white;
                text-align: center;
            }
            td {
                text-align: left;
            }
            pre {
                white-space: pre-wrap; /* 确保长文本自动换行 */
            }
            .type-column {
                text-align: center;
                width: 5%;
                min-width: 75px;
                max-width: 200px;
                white-space: pre-wrap; /* 确保长文本自动换行 */
                word-wrap: break-word;
            }
            .url-column {
                width: 10%;
                min-width: 100px;
                max-width: 200px;
                white-space: pre-wrap; /* 确保长文本自动换行 */
                word-wrap: break-word;
            }
            .req-column {
                width: 25%;
                min-width: 200px;
                max-width: 400px;
                white-space: pre-wrap; /* 确保长文本自动换行 */
                word-wrap: break-word;
            }
            .rsp-column {
                width: 25%;
                min-width: 200px;
                max-width: 400px;
                white-space: pre-wrap; /* 确保长文本自动换行 */
                word-wrap: break-word;
            }
            h1 {
                color: #2864dd;
                margin-bottom: 30px;
            }
        </style>
    </head>
    <body>
        <h1>BOLAFuzz</h1>
        <div class="container">
            <table>
                <tr>
                    <th class="type-column">漏洞类型</th>
                    <th class="url-column">漏洞API</th>
                    <th class="req-column">请求数据包</th>
                    <th class="rsp-column">返回数据包</th>
                </tr>
                {rows}
            </table>
        </div>
    </body>
    </html>
    """
    # 生成表格行
    rows = ""
    for vuln in my_list:
        rows += f"""
            <tr>
                <td class="type-column"><pre>{vuln['result']['reason']}</pre></td>
                <td class="url-column"><pre>{vuln['result']['url']}</pre></td>
                <td class="req-column"><pre>{vuln['request']}</pre></td>
                <td class="rsp-column"><pre>{vuln['response']}</pre></td>
            </tr>
        """

    # 插入表格行到模板
    html_content = template.replace("{rows}", rows)

    # 写入HTML文件
    with open('./output/output.html', 'w', encoding='utf-8') as file:
        file.write(html_content)

    print("HTML文件已生成。")