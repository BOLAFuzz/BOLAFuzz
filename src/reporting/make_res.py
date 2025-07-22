import json
def make_res(json_str):
    json_str = json_str.replace("'", '"')

    # 2. 移除多余的空格和换行符
    json_str = json_str.replace("\n        ", "")
    json_str = json_str.replace("True", "true")
    json_str = json_str.replace("False", "false")
    # 将JSON字符串转换为字典
    data = json.loads(json_str)
    with open('data.json', 'a') as f:  # 注意这里的模式是 'a' 而不是 'w'
        f.write(json_str + '\n')  # 添加换行符以分隔每次追加的内容
