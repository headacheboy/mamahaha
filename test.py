# -*- coding: utf-8 -*-

import re
import os
import pyltp
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import NamedEntityRecognizer
from pyltp import Parser
from pyltp import SementicRoleLabeller
from pyltp import VectorOfParseResult
from pyltp import ParseResult
import jieba
import re
LTP_DATA_DIR = 'D:\project\ltp-data-v3.3.1\ltp_data'  # ltp模型目录的路径
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')  # 分词模型路径，
# 模型名称为`cws.model`
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，
# 模型名称为`pos.model`
ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')  # 命名实体识别模型路径，
# 模型名称为`ner.model`
par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')  # 依存句法分析模型路径
# 模型名称为`parser.model`
srl_model_path = os.path.join(LTP_DATA_DIR,'srl') # 语义角色标注模型

segmentor = Segmentor()  # 初始化实例
segmentor.load(cws_model_path)  # 加载模型
postagger = Postagger()
postagger.load(pos_model_path)
recognizer = NamedEntityRecognizer() # 初始化实例
recognizer.load(ner_model_path)  # 加载模型
parser = Parser()
parser.load(par_model_path)
labeller = SementicRoleLabeller()
labeller.load(srl_model_path)

s = '红绿蓝三种颜色混合是白色'
words  = list(segmentor.segment(s))
postags = list(postagger.postag(words))
print(list(words))
print(list(postags))
arcs = parser.parse(list(words),list(postags))
print(len(arcs))
print("\t".join("%d:%s" % (arc.head, arc.relation) for arc in arcs))
netags = recognizer.recognize(words, postags)  # 命名实体识别
print(list(netags))
# roles = labeller.label(words,postags,arcs)
#
# for role in roles:
#     print( role.index, "".join(
#         ["%s:(%d,%d)" % (arg.name, arg.range.start, arg.range.end) for arg in role.arguments]))


# pattern = re.compile('“(.*?)”')
# pattern2 = re.compile('"(.*?)"')
# myStr = '出自“毛泽东”《长征》“金沙水拍云崖暧”的下一句是'
# a = pattern.findall(myStr)
# a.extend(pattern2.findall(myStr))
# print (a)
# from pyltp import SentenceSplitter
# sents = SentenceSplitter.split('金沙水拍云崖暖，大渡桥横铁索寒。')  # 分句
# print (list(sents))
#
# ans = '金沙水拍云崖暖，大渡桥横铁索寒。'
# sen = '大渡桥横铁索寒'
# punc_lst = [',','.','?','，','。','？','!','！']
# index = ans.find(sen)
# end_index = -1
# start_index = -1
# for i in range(index,-1,-1):
#     if ans[i] in punc_lst:
#         end_index = i
#         break
# for i in range(end_index-1,-1,-1):
#     if ans[i] in punc_lst:
#         start_index = i
#         break
# print( ans[start_index+1:end_index])

# from jieba import analyse
# # 引入TF-IDF关键词抽取接口
# tfidf = analyse.extract_tags
#
# # 原始文本
# text = "红绿蓝三种颜色混合是白色的"
#
# # 基于TF-IDF算法进行关键词抽取
# keywords = tfidf(text)
# print ("keywords by tfidf:")
# # 输出抽取出的关键词
# print(type(keywords))
# print(type(list()))
# for keyword in keywords:
#     print (keyword + "/",)

s = '这回一共有一千一百个人'
p = re.compile("([\d|零|一|二|三|四|五|六|七|八|九|十|百|千|万|亿]+)个")
print(p.findall(s))