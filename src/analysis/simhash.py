import jieba
import jieba.analyse
import numpy as np


class Simhash(object):
    def simhash(self, content):
        keylist = []
        # jieba分词
        seg = jieba.cut(content)
        # 去除停用词永祥
        # jieba.analyse.set_stop_words("stopwords.txt")
        # 得到前20个分词和tf-idf权值
        keywords = jieba.analyse.extract_tags("|".join(seg), topK=20, withWeight=True, allowPOS=())
        print(keywords)
        for feature, weight in keywords:
            print(weight)
            weight = int(weight * 20)
            print(weight)
            print("k="+feature)
            feature = self.string_hash(feature)
            print("v="+feature)
            temp = []
            for i in feature:
                if i == "1":
                    temp.append(weight)
                else:
                    temp.append(-1 * weight)
            keylist.append(temp)


        list1 = np.sum(np.array(keylist), axis=0)
        if keylist == []:
            return "00"
        simhash = ""
        # 降维处理
        for i in list1:
            if i > 0:
                simhash += "1"
            else:
                simhash += "0"
        return simhash

    def string_hash(self, source):
        if source == "":
            return 0
        else:
            x = ord(source[0]) << 7
            m = 1000003
            mask = 2 ** 128 - 1
            for c in source:
                x = ((x * m) ^ ord(c)) & mask
            x ^= len(source)
            if x == -1:
                x = -2
            x = bin(x).replace('0b', '').zfill(64)[-64:]
        return str(x)

def hammingDis(s1,s2):
    t1 = "0b" + s1
    t2 = "0b" + s2
    n = int(t1,2) ^ int(t2,2)
    i = 0
    print(bin(n))
    while n:
        n &= (n-1)
        i += 1
    print(i)
    max_hashbit = max(len(bin(int(t1,2))), len(bin(int(t2,2))))
    sim = i/max_hashbit
    print(sim)