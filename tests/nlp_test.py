# -*-coding:utf-8 -*-
import torch
from transformers import BertTokenizer

def run(argument=None):
    # 加载整个模型对象
    model = torch.load('model_full_11.pth', weights_only=False, map_location=torch.device('cpu'))
    model.eval()

    text = "91263"
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    input_tensor= tokenizer(text, return_tensors="pt")

    # 进行预测
    with torch.no_grad():
        output = model(**input_tensor)
        logits = output.logits

    # 获取预测类别
    predicted_label = torch.argmax(logits, dim=1).item()
    print(f"predicted label: {predicted_label}")

    return predicted_label

run()