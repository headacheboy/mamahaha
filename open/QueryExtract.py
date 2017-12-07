import re
import jieba

class QueryExtract():
    def __init__(self):
        self.words = []
        self.quotePattern = re.compile(r"“(.*?)”|《(.*?)》|”(.*?)“")
        self.next_sentence = ["下一句", "上一句", "前一句", "后一句"]
        self.stopwords = []
        file = open("zh_stopword.txt", encoding='utf-8')
        for line in file:
            string = line.split()[0]
            self.stopwords.append(string)

    def getWords(self, sentence):
        self.words.clear()
        for ele in self.next_sentence:
            if sentence.find(ele) != -1:
                ls = re.findall(self.quotePattern, sentence)
                for e in ls:
                    if len(e[0]) != 0:
                        self.words.append(e[0])
                        self.words.append(ele)
                        return
                    elif len(e[2]) != 0:
                        self.words.append(e[2])
                        self.words.append(ele)
                        return

        ls = re.findall(self.quotePattern, sentence)
        for ele in ls:
            for e in ele:
                if len(e) != 0:
                    self.words.append(e)
        sentence = re.sub(self.quotePattern, "", sentence)
        ls = jieba.cut(sentence)
        for ele in ls:
            if ele not in self.stopwords:
                self.words.append(ele)

if __name__ == "__main__":
    query = QueryExtract()
    query.getWords("国家5A级旅游景区“瘦西湖”位于哪个城市？"
                   "")
    print((query.words))