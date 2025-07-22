# -*-coding:utf-8 -*-
import csv
import torch
from torch.optim import AdamW
from tqdm import tqdm
from transformers import BertTokenizer, BertForSequenceClassification
from torch.utils.data import DataLoader, TensorDataset


# 读取数据
datas = []
labels = []
with open('data.csv', mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)
    # 遍历CSV文件中的每一行
    for row in reader:
        if row[0] != 'data':
            datas.append(row[0])
            labels.append(int(row[1]))

# 加载预训练的BERT模型和tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=11)

# 对数据进行tokenize和padding
inputs = tokenizer(datas, padding=True, truncation=True, return_tensors="pt")
labels = torch.tensor(labels)

# 构建数据集和数据加载器
dataset = TensorDataset(inputs['input_ids'], inputs['attention_mask'], labels)
dataloader = DataLoader(dataset, batch_size=8, shuffle=True)

# 定义优化器和损失函数
learning_rate = 1e-6
optimizer = AdamW(model.parameters(), lr=learning_rate)
loss_fn = torch.nn.CrossEntropyLoss()

# 训练模型
epochs = 10
for epoch in range(epochs):
    total_loss = 0.0
    model.train()  # 设置模型为训练模式
    for batch in tqdm(dataloader):
        optimizer.zero_grad()
        input_ids, attention_mask, label = batch
        outputs = model(input_ids, attention_mask=attention_mask, labels=label)
        loss = loss_fn(outputs.logits, label)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    avg_loss = total_loss / len(dataloader)
    print(f"Epoch {epoch+1}, Loss: {avg_loss:.4f}")

# 保存模型
torch.save(model, 'model_full_11.pth')
