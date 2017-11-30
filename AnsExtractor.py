# -*- coding: utf-8 -*-

import re
import os
import pyltp
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import NamedEntityRecognizer
from pyltp import Parser
from pyltp import VectorOfParseResult
from pyltp import ParseResult
#from pyltp import 

LTP_DATA_DIR = 'E:\\LTP\\ltp-data-v3.3.1\\ltp_data\\'  # ltp模型目录的路径
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')  # 分词模型路径，
# 模型名称为`cws.model`
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，
# 模型名称为`pos.model`
ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')  # 命名实体识别模型路径，
# 模型名称为`ner.model`
par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')  # 依存句法分析模型路径
# 模型名称为`parser.model`

# 句法树的一个结点
class Node(object):
    def __init__(self):
        pass

# 一个句子的句法树
class Sentence_Tree(object):
    def __init__(self, arcs):
        pass
        

# 答案提取模块类
class AnsExtractor(object):
    def __init__(self, sents, key_words, ques_type, ques):
        self.sentences = sents # 候选答案句集合
        self.key_words = key_words # 关键词集合
        self.question_type = ques_type # 问题种类
        self.question = ques # 处理后的问句（或问句集合？）
        
        self.segmentor = Segmentor()  # 初始化实例
        self.segmentor.load(cws_model_path)  # 加载模型
        self.postagger = Postagger()
        self.postagger.load(pos_model_path)
        self.recognizer = NamedEntityRecognizer() # 初始化实例
        self.recognizer.load(ner_model_path)  # 加载模型
        self.parser = Parser()
        self.parser.load(par_model_path)
        
        self.stop_words = []
        # self.sim_cloud_types = []
        self.sim_word_code = {} # 每个词有一个list
        self.a = 0.8
        self.b = 0.2 # 这俩是参数，先就这么干吧
        self.get_sim_cloud()
        
    # 读取同义词词林
    """
    同义词词林中的词有三种关系，同义、相关（不一定同义）、独立词
    如果用于计算相似度的话，相关的词语具有相同的code，也是能接受的
    """
    def get_sim_cloud(self):
        sim_file = open("similarity.txt", 'r', encoding = "utf-8")
        lines = sim_file.readlines(1000000)
        # 对行按格式进行处理
        for line in lines:
            code = line[0:7]
            the_type = line[7]
            words = line[9:]
            words = words.split(' ')
            # 解析过的一行，放进模型
            for word in words:
                if word in self.sim_word_code:
                    self.sim_word_code[word].append(code)
                else:
                    self.sim_word_code[word] = []
                    self.sim_word_code[word].append(code)
        sim_file.close()
        pass
    
    # 计算候选答案句与问句的相似度，并返回排序后相似度最高的五个句子
    def sort_sentences(self):
        # 首先得到问句的c&r词集
        question_cr_words = self.get_centrial_and_rela_words(self.question)
        sims = []
        i = 0
        for sentence in self.sentences:
            sim = self.calc_similarity(sentence, question_cr_words)
            sims.append((i, sim))
            i = i+1
        sims.sort(key = lambda item:item[1], reverse = True)
        print(sims)
        ans_sentences = []
        for i in range(0, 5):
            ans_sentences.append(self.sentences[sims[i][0]])
        return ans_sentences
    
    # 句法分析，得到一个句子的核心词和依附于核心词的词的集合
    def get_centrial_and_rela_words(self, sentence):
        words = self.segmentor.segment(sentence) # 分词
        print(' '.join(words))
        postags = self.postagger.postag(words) # 词性标注
        print(' '.join(postags))
        arcs = self.parser.parse(words, postags) # 句法分析
        i = 1 # 临时变量，指示句法树当前结点
        layer_2 = [] # 句法树第二层结点索引
        layer_3 = [] # 句法树第三层结点索引
        for arc in arcs:
            print("%d<--%d:%s" % (i, arc.head, arc.relation))
            # 额外的自然语言处理方案——规则补充的句法分析
            """
            添加几条规则
            1、对表示时间的词进行处理时，去掉时间词之间的依存关系，把连续的时间词看成一个整体。
            2、对助词进行处理，去除句子中助词词性的词，
            如“的”、“地”和“得”，然后将依附这些助词的词语直接依附到这些助词所依附的词语上
            即不改变弧的方向，然后把其它两个词语直接相连
            但是如果依附于这些助词的词语有很多不是唯一的,则此规则不能进行。 
            3、对虚词进行处理，根据前文所做的词性标注处理,去除与句子意思不相关的
            虚词，所依据的规则如上。 
            """
            # 时间有限，还没实现这些规则。。。
            # HED表示，这个词是核心词
            if arc.relation == "HED":
                centrial_word = i # 核心词
            i = i+1
        i = 1
        for arc in arcs:
            if arc.head == centrial_word:
                layer_2.append(i) # 找到第2层节点
            i = i+1
        i = 1
        for arc in arcs:
            if arc.head in layer_2:
                layer_3.append(i) # 找到第三层结点
            i = i+1
        # 找核心词 & 依附于核心词的词语
        # 目前没做上面几条规则处理，除了核心词，把第二第三层的词都算作依附于核心词
        rela_words = []
        # 规定：rela_words数组的第一个词是核心词
        rela_words.append(words[centrial_word-1])
        for j in layer_2:
            rela_words.append(words[j-1])
        for j in layer_3:
            rela_words.append(words[j-1])
        return rela_words
    
    # 计算两个词语的语义距离
    # Dist(A,B) = min{dist(m,n)}
    # dist(m,n) = 2 * (7 - first_diff)
    def calc_Dist(self, codes1, codes2):
        dist = 14
        for code1 in codes1:
            for code2 in codes2:
                first_diff = 7
                for i in range(0, 7):
                    if code1[i] != code2[i]:
                        first_diff = i
                        break
                tmp_dist = 2 * (7 - first_diff)
                if tmp_dist < dist:
                    dist = tmp_dist
        return dist
    
    # 计算某句子与问句的相似度
    def calc_similarity(self, sentence, question_cr_words):
        # 对句子进行句法分析，得到c&r词集
        cr_words = self.get_centrial_and_rela_words(sentence)
        # 计算核心词相似度
        if question_cr_words[0] in self.sim_word_code:
            question_c_codes = self.sim_word_code[question_cr_words[0]]
        else:
            question_c_codes = ["Dk06D01"] # 注：这个码为 谜、谜语。。。
        if cr_words[0] in self.sim_word_code:
            c_codes = self.sim_word_code[cr_words[0]]
        else:
            c_codes = ["Dk06D01"]
        c_Dist = self.calc_Dist(question_c_codes, c_codes)
        if c_Dist == 0:
            c_sim = 1
        else:
            c_sim = 7 / (7 + c_Dist)
        
        # 计算非核心词相似度
        question_r_codes = [0] * (len(question_cr_words) - 1)
        for i in range(1, len(question_cr_words)):
            if question_cr_words[i] in self.sim_word_code:
                question_r_codes[i-1] = self.sim_word_code[question_cr_words[i]]
            else:
                question_r_codes[i-1] = ["Dk06D01"]
        r_codes = [0] * (len(cr_words) - 1)
        for i in range(1, len(cr_words)):
            if cr_words[i] in self.sim_word_code:
                r_codes[i-1] = self.sim_word_code[cr_words[i]]
            else:
                r_codes[i-1] = ["Dk06D01"]
        # 这个略麻烦一点
        q_s_sims = [0] * (len(question_cr_words) - 1)
        q_s_sim = 0
        for i in range(0, len(question_r_codes)):
            for j in range(0, len(r_codes)):
                tmp_Dist = self.calc_Dist(question_r_codes[i], r_codes[j])
                if tmp_Dist == 0:
                    q_s_sims[i] = 1
                else:
                    tmp_sim = 7 / (7 + tmp_Dist)
                    if tmp_sim > q_s_sims[i]:
                        q_s_sims[i] = tmp_sim
            q_s_sim += q_s_sims[i]
        q_s_sim = q_s_sim / len(question_r_codes)
        
        s_q_sims = [0] * (len(cr_words) - 1)
        s_q_sim = 0
        for i in range(0, len(r_codes)):
            for j in range(0, len(question_r_codes)):
                tmp_Dist = self.calc_Dist(r_codes[i], question_r_codes[j])
                if tmp_Dist == 0:
                    s_q_sims[i] = 1
                else:
                    tmp_sim = 7 / (7 + tmp_Dist)
                    if tmp_sim > s_q_sims[i]:
                        s_q_sims[i] = tmp_sim
            s_q_sim += s_q_sims[i]
        s_q_sim = s_q_sim / len(r_codes)
        
        res = self.a * c_sim + self.b * ((q_s_sim + s_q_sim) / 2)
        return res
    
    # 得到问题的答案
    def get_ans(self):
        ans_sentences = self.sort_sentences()
        print(ans_sentences)
        ans = ans_sentences[0]
        if self.question_type == "人物":
            # 这里需要命名实体识别
            # 先直接怼吧
            words = self.segmentor.segment(ans) # 分词
            postags = self.postagger.postag(words) # 词性标注
            netags = self.recognizer.recognize(words, postags)  # 命名实体识别
            final_anses = []
            tmp_str = ""
            for i in range(len(netags)):
                if netags[i] == "S-Nh":
                    final_anses.append(words[i])
                if netags[i] == "B-Nh":
                    tmp_str = words[i]
                if netags[i] == "I-Nh":
                    tmp_str += words[i]
                if netags[i] == "E-Nh":
                    tmp_str += words[i]
                    final_anses.append(tmp_str)
            print(final_anses)
        if len(final_anses) == 0:
            return "无法回答此问题"
        else:
            return final_anses[0]

#test_sentences = ["《资治通鉴》是我国古代著名史学家、政治家司马光和他的助手刘攽、刘恕、范祖禹、司马康等人历时十九年编纂的一部规模空前的编年体通史巨著",
#                  "《资治通鉴》（常简作《通鉴》）是由北宋司马光主编的一部多卷本编年体史书",
#                  "《资治通鉴》是司马光及其助刘攽、刘怒、范祖禹等根据大量的史料编纂而成的一部编年体史书",
#                  "《资治通鉴》是由北宋司马光主编的一部多卷本编年体史书",
#                  "史记的作者是司马迁",
#                  "《论语》这类书比作教材中的公式概念,把《资治通鉴》比作试题",
#                  "想买一套《史记》和《资治通鉴》,求推荐版本",
#                  " 姜鹏品读《资治通鉴》"]
#ans_extractor = AnsExtractor(test_sentences, "", "人物", "资治通鉴的作者是")
## 下面这个函数相当于模块的入口和出口，直接用就行
#answer = ans_extractor.get_ans()
#del(ans_extractor)


test_sentences = ["木婉清的母亲秦红棉被段正淳负心后伤心欲绝",
                  "《天龙八部》中段誉和木婉清的爱情故事",
                  "木婉清,金庸武侠小说《天龙八部》中的人物",
                  "天龙八部(世纪新修版)书中最后一段介绍了木婉清被册封为贵妃。",
                  "木婉清同父异母的姐姐是王语嫣",
                  "木婉清的个性里沿袭了一部分母亲的执着和父亲的多情",
                  "《天龙八部》中木婉清的饰演者有很多,最近的就有赵圆瑗、蒋欣等",
                  "秦红棉，金庸武侠小说《天龙八部》中的人物，外号修罗刀,是木婉清的母亲"]
ans_extractor = AnsExtractor(test_sentences, "", "人物", "金庸小说《天龙八部》中，木婉清的母亲是谁")
answer = ans_extractor.get_ans()
print(answer)