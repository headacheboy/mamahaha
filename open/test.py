import urllib.request
import urllib.parse
import string
import re

pattern = re.compile(r"<tr><td><font color=\"red\">1</font></td><td><font color=\"red\">(.*?)</font></td><td><font color=\"red\">1.0</font></td></tr>")

def getAns():
    fileO = open("output_time_number", "w", encoding='utf-8')
    file = open("test.txt", encoding='utf-8')
    qType = open("questionType", encoding='utf-8')
    loop = 0
    for line, type in zip(file, qType):
        loop += 1
        type = type.split()[0]
        if type != "NUMBER" and type != "TIME":
            fileO.write("testing\n")
            continue
        line = line.replace(" ", "%20")
        dic = 'http://localhost:8080/index.jsp?q='+line
        url = urllib.parse.quote(dic, safe=string.printable)
        #req = urllib.request.Request(url)
        data = urllib.request.urlopen(url).read()
        # self.data = gzip.decompress(self.data)
        data = data.decode('utf-8', 'ignore')

        ans = re.findall(pattern, data)
        print(line, ans)
        if len(ans) == 0:
            fileO.write("testing\n")
        else:
            fileO.write(ans[0] + "\n")

getAns()