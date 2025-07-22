# -*-coding:utf-8 -*-
import random

mutate_dict = {
    'id': '77875',
}


def mutate_id(param, flag):
    # 首先尝试使用字典替换
    if param in mutate_dict:
        return mutate_dict[param], True

    # 如果flag为False或者替换失败，则尝试数值加减
    if not flag:
        # 假设ID是数字类型
        if isinstance(param, int):
            # 随机决定增加还是减少
            operation = random.choice(['+', '-'])
            # 随机决定增加或减少的量，这里以1到10之间的随机数为例
            change_amount = random.randint(1, 10)
            if operation == '+':
                new_param = param + change_amount
            else:
                new_param = param - change_amount
            return new_param, True
        else:
            # 如果param不是数字类型，返回原值和False
            return param, False
    else:
        # 如果flag为True，直接返回原值和True
        return param, True


# 使用示例
param = 123  # 假设param是一个数字
flag = False
new_param, new_flag = mutate_id(param, flag)
print(f"New Param: {new_param}, New Flag: {new_flag}")