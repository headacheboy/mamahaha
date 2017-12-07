import urllib.request
import urllib.parse
import string
import re
import QueryExtract

class Crawler():
    def __init__(self):
        self.stopwords = set()
        self.data = None
        self.prefix = "http://www.baidu.com/s?"
        self.path = "unlabel"
        self.output = "output"
        self.fileO = open(self.output, "w", encoding='utf-8')
        self.pattenAnsStr = re.compile("<div class=\"op_exactqa_s_answer\">(.*?)</div>", re.DOTALL)
        self.patternAnsStrDetail = re.compile("<div class=\"op_exactqa_detail_s_answer\">(.*?)</div>", re.DOTALL)
        self.patternAnsStrDetailStr = re.compile("<span>(.*?)</span>", re.DOTALL)
        self.patternRemove = re.compile("<.*?>|\[.*?\]")
        self.patternRemoveSpan = re.compile("<span.*?</span>")
        self.patternRemoveA = re.compile("<a.*?</a>")
        self.patternQuote = re.compile(r"“(.*?)”|”(.*?)“")
        self.patternPassage = re.compile("<div class=\"c-abstract\">(.*?)</div>")
        self.abbr = ["全称", "简称"]
        self.headers = {'User-Agent': 'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) '
                                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
                        }
        self.patternPunc = re.compile("[\.;。；,，？\?\\\哦吗呢呵啊呀/!！…]")
        self.queryExtract = QueryExtract.QueryExtract()

    def getResponse(self, word):
        dic = self.prefix+"wd="+word
        url = urllib.parse.quote(dic, safe=string.printable)
        req = urllib.request.Request(url, headers=self.headers)
        self.data = urllib.request.urlopen(req).read()
        #self.data = gzip.decompress(self.data)
        self.data = self.data.decode('utf-8', 'ignore')

    def getAns(self):
        noAns = 0
        file = open(self.path, encoding='utf-8')
        loop = 0
        for line in file:
            loop += 1
            print(loop)
            if len(line.split()) > 1:
                line = "".join(line.split())
            self.queryExtract.getWords(line)
            word = "%20".join(self.queryExtract.words)
            self.getResponse(word)
            ls = re.findall(self.pattenAnsStr, self.data)
            if len(ls) != 0:
                flag = False
                for ele in self.abbr:
                    if line.find(ele)  != -1:
                        flag = True
                        break
                if not flag:
                    # for answer_s
                    string = ls[0]
                    string = re.sub(self.patternRemove, " ", string)
                    ls = string.split()
                    #print(line, ls)
                    if self.output is not None:
                        self.fileO.write(word + "\t" + ls[0] + "\n\n")
                        self.fileO.flush()
                    continue
            ls = re.findall(self.patternAnsStrDetail, self.data)
            if (len(ls) != 0):
                flag = False
                for ele in self.abbr:
                    if line.find(ele) != -1:
                        flag = True
                        break
                if not flag:
                    # for detail_answer_s
                    string = ls[0]
                    #string = re.findall(self.patternAnsStrDetailStr, string)[0]
                    string = re.sub(self.patternRemove, "", string)
                    string = re.sub(self.patternPunc, " ", string)
                    ls = string.split()
                    #print(line, ls)
                    if self.output is not None:
                        self.fileO.write(word + "\t" + ls[0] + "\n\n")
                        self.fileO.flush()
                    continue
            ls = re.findall(self.patternPassage, self.data)
            if len(ls) != 0:
                #for passage retrieval
                for ind, ele in enumerate(ls):
                    ele = re.sub(self.patternRemoveSpan, " ", ele)
                    ele = re.sub(self.patternRemoveA, " ", ele)
                    ls[ind] = re.sub(self.patternRemove, "", ele)
                    ele = re.sub(self.patternPunc, " ", ls[ind])
                    #if len(ele.split()) == 1 and len(re.findall("[()A-Za-z]", ele.split()[0])) != len(ele.split()[0]):
                    if self.output is not None:
                        self.fileO.write(word + "\t" + ls[ind] + "\n")
                        self.fileO.flush()
                    #print(line, ls[ind])
                self.fileO.write("\n")

if __name__ == "__main__":
    crawler = Crawler()
    crawler.getAns()