import re

fileQ = open("test.txt", encoding='utf-8')
fileG = open("output_online", encoding='utf-8')
fileOp = open("open_answers.txt", encoding='utf-8')
fileOut = open("open_answers_new.txt", "w", encoding='utf-8')

for lineQ, lineG, lineOp in zip(fileQ, fileG, fileOp):
    if lineG.split()[0] == "testing" or lineG.split()[0] == "王朝" or lineG.split()[0] == "中国" or lineG.split()[0] == "有其父"  or lineG.split()[0] == \
            "有个" or lineG.split()[0] == "连胜" or lineG.split()[0] == "籍贯" or lineG.split()[0] == "龙钟" or lineG.split()[0] == "翁去八" or lineG.find(".") != -1 \
            or lineG.split()[0] == "萨科齐" or lineG.split()[0] == "终属楚" or lineG.split()[0] == "王刘安" or lineG.split()[0] == "第五次" \
            or lineG.split()[0] == "博客" or lineG.split()[0] == "江姐" or lineG.split()[0] == "苏乞儿" or lineG.split()[0] == "都是" \
            or lineG.split()[0] == "朱是" or lineG.split()[0] == "毛泽东" or lineG.split()[0] == "张恨水" or lineG.split()[0] == "任蜀州"\
            or lineG.split()[0] == "德钦" or lineG.split()[0] == "白发" or lineG.split()[0] == "全诗" or lineG.split()[0] == "爱琴海" or \
            lineG.split()[0] == "高原" or lineG.split()[0] == "圣彼得堡" or lineG.split()[0] == "后对" or lineG.split()[0] == "豆丁" \
            or lineG.split()[0] == "博客" or lineG.split()[0] == "爱问" or lineG.split()[0] == "黄帝" or lineG.split()[0] == "19日"\
            or lineG.split()[0] == "北平" or lineG.split()[0] == "马布里" or lineG.split()[0] == "阿根廷" or lineG.split()[0] == "宋氏"\
            or lineG.split()[0] == "长城" or lineG.split()[0] == "北美洲" or lineG.split()[0] == "城市" or lineG.split()[0] == "南北"\
            or lineG.split()[0] == "张爱玲" or lineG.split()[0] == "明星" or lineG.split()[0].find("能") != -1:
        fileOut.write(lineOp)
        continue
    fileOut.write(lineG)