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
from jieba import analyse

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

# 答案提取模块类
class AnsExtractor(object):
    
    # 修改了init函数，传进来的句子、关键字等参数不再作为init函数的参数
    # init做的事情只有：
    # 1、加载模型
    # 2、加载同义词词林
    # 其他参数传递给主流程函数do_ans_extract
    def __init__(self):
        self.segmentor = Segmentor()  # 初始化实例
        self.segmentor.load(cws_model_path)  # 加载模型
        self.postagger = Postagger()
        self.postagger.load(pos_model_path)
        self.recognizer = NamedEntityRecognizer() # 初始化实例
        self.recognizer.load(ner_model_path)  # 加载模型
        self.parser = Parser()
        self.parser.load(par_model_path)
        self.labeller = SementicRoleLabeller()
        self.labeller.load(srl_model_path)
        self.istime_lst = ['年份是',"时间是"]
        self.iscolor_lst = ['什么颜色',"哪种颜色","哪个颜色"]
        self.unit_lst = ["回","对","山","只","刀","群","江","条","个","打","尾","手","双","张","溪","挑","坡","首","令","网","辆","座","阵","队",
                         "顶","匹","担","墙","壳","炮","场","扎","棵","支","颗","钟","单","曲","客","罗","岭","阙",
                         "捆","丘","腔","贯","袭","砣","窠","岁","倍","枚","次"]
        self.islocation_lst = ['哪个城市',"哪个国家",'国籍是',"什么国籍","哪个省","哪座城市"]
        self.isorganization_lst = ['哪个组织',"组织是"]
        self.isperson_lst = ['哪个皇帝',"是谁","什么名字","者是"]
        self.isnum_lst = list()
        for unit in self.unit_lst:
            self.isnum_lst.append("多少"+unit)
        
        self.stop_words = [] # 停用词目前还没用到
        self.sim_word_code = {} # 每个词有一个list，是它的编码（可能多个）
        self.get_sim_cloud()
        
    # 读取同义词词林
    """
    同义词词林中的词有三种关系，同义、相关（不一定同义）、独立词
    如果用于计算相似度的话，相关的词语具有相同的code，也是能接受的
    所以并没有区分词关系，而是直接读取了词的code
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

    def get_all_NER(self,ans_sentence,type):
        '''
        得到答案中的所有某一类型的命名实体
        :param ans_sentence: 答案句子
        :param type: 命名实体类型
        :return: 该类型的所有命名实体集合
        '''
        words = self.segmentor.segment(ans_sentence)  # 分词
        postags = self.postagger.postag(words)  # 词性标注
        netags = self.recognizer.recognize(words, postags)  # 命名实体识别

        ner_lst = list() # 命名实体集合
        temp_str = ''
        for i in range(len(netags)):
            if netags[i] == 'S-'+ type:
                ner_lst.append(words[i])
            elif netags[i] == 'B-' + type:
                temp_str = words[i]
            elif netags[i] == 'I-' + type:
                temp_str += words[i]
            elif netags[i] == 'E-' + type:
                temp_str += words[i]
                ner_lst.append(temp_str)
        return ner_lst

    def get_pos_lst(self,sentence,type):
        '''
        获得句子中的某种词性集合
        :param sentence:
        :return: 返回词性集合
        '''
        words = list(self.segmentor.segment(sentence))
        postags = list(self.postagger.postag(words))

        temp_tag = ''
        postag_lst = list()
        for i in range(len(postags)):
            if postags[i] == type:
                temp_tag += words[i]
            else:
                if temp_tag != '':
                    postag_lst.append(temp_tag)
                    temp_tag = ''
        return postag_lst

    def get_context_type(self,ques):
        '''
        判断问题类型 是上一句还是下一句
        :param ques: 问题语句
        :return: '上句' '下句'
        '''
        next_word = ['下句','下一句','下文','后文']
        for word in next_word:
            if ques.find(word) != -1:
                return '下文'
        return '上文'

    def get_parse_oneclass(self,sent):
        '''
        获得句子的第二层 节点
        :param sent:
        :return:返回词语及其依存关系
        '''
        words = list(self.segmentor.segment(sent))
        postags = list(self.postagger.postag(words))
        arcs = self.parser.parse(words,postags)
        result_arc = dict()
        # 依存关系的下标 是从1开始的   0表示root
        i = 0
        for arc in arcs:
            if arc.head == 0:
                root = {'word':words[i],'rel':arc.relation,'rel_index':i+1,'tag':postags[i]}
                head = words[i]
            i = i + 1
        i = 0
        for arc in arcs:
            if arc.head == root['rel_index']:
                result_arc[words[i]] = {'rel':arc.relation,'tag':postags[i]}
            i = i+1

        return head,result_arc

    def list_has_intersection(self,lsta,lstb):
        '''
        lstb中的单词 有否存在某一个单词  是lsta的某个单词  子串
        :param lsta:
        :param lstb:
        :return: lsta的某个单词
        '''
        for wa in lsta:
            for wb in lstb:
                if wa.find(wb) > -1:
                    return wa
        return None

    def get_arc_by_index(self,arcs,index):
        '''
        根据index 得到arc
        :param index: 这里的index 与语法依存树保持一致  即从1开始
        :return: arc
        '''
        i = 1
        for arc in arcs:
            if i == index:
                return arc
            i = i + 1

    def has_spe_words(self,text,lst):
        '''
        用于判断某句话里面 是否有列表中的单词
        :param text:
        :param lst:
        :return:
        '''
        for word in lst:
            if text.find(word) > -1:
                return True
        return  False

    def get_core_rel(self,arcs,words,word):
        index = words.index(word) + 1
        arc = self.get_arc_by_index(arcs,index)
        while(arc.relation == 'ATT'):
            arc = self.get_arc_by_index(arcs,arc.head)
        arc = self.get_arc_by_index(arcs,arc.head)
        return arc






    # 调用答案抽取算法，主流程函数，返回即为答案
    def do_ans_extract(self, sents, key_words, ques_type, ques, a, b):
        self.sentences = sents # 候选答案句集合
        self.key_words = key_words # 关键词集合
        self.question_type = ques_type # 问题种类
        self.question = ques # 处理后的问句（或问句集合？）
        self.a = a
        self.b = b # 相似度计算算法的两个参数

        if self.has_spe_words(self.question,self.isnum_lst):
            self.question_type = "NUMBER"
            ques_type = "NUMBER"
        elif self.has_spe_words(self.question,self.iscolor_lst):
            self.question_type = "COLOR"
            ques_type = "COLOR"
        elif self.has_spe_words(self.question,self.istime_lst):
            self.question_type = "TIME"
            ques_type = "TIME"
        elif self.has_spe_words(self.question,self.islocation_lst):
            self.question_type = "LOCATION"
            ques_type = "LOCATION"
        elif self.has_spe_words(self.question,self.isperson_lst):
            self.question_type = "PERSON"
            ques_type = "PERSON"

        # 去掉候选答案句中的空白字符
        for i in range(len(self.sentences)):
            self.sentences[i] = ''.join(self.sentences[i].split())
        # 首先得到五个最有可能包含答案的句子
        ans_sentences = self.sort_sentences() # !!!暂时停用
        # ans_sentences = self.sentences
        # print(ans_sentences)
        
        # 然后根据问题类型，在这五个句子中进行答案抽取
        ans = ans_sentences[0]
        # print(ans)

        # print(self.get_all_NER(ques,'Nh'))
        if self.question_type == "PERSON":
            # 这里需要命名实体识别
            # 先直接怼吧
            final_anses = self.get_all_NER(ans,'Nh')
            # if self.question == "唯一获得香港电影金像奖最佳女配角的中国大陆演员是？":
            #     print(ans)
            for item in final_anses:
                if ques.find(item) == -1:
                    return item
            if len(final_anses) == 0:
                return ans
            else:
                return final_anses[0]
        elif self.question_type == 'LOCATION':
            final_anses = self.get_all_NER(ans, 'Ns')
            # print(final_anses)
            for item in final_anses:
                if ques.find(item) == -1:
                    return item
            if len(final_anses) == 0:
                return ans
            else:
                return final_anses[0]
        elif self.question_type == 'ORGANIZATION':
            final_anses = self.get_all_NER(ans, 'Ni')
            # print(final_anses)
            for item in final_anses:
                if ques.find(item) == -1:
                    return item
            if len(final_anses) == 0:
                return ans
            else:
                return final_anses[0]
        elif self.question_type == 'NUMBER' :
            for sentence in ans_sentences:
                for num_word in self.isnum_lst:
                    if self.question.find(num_word) > -1:
                        pattern = re.compile("([\d|零|一|二|三|四|五|六|七|八|九|十|百|千|万|亿]+){unit}".format(unit=num_word[-1]))
                        final_anses = pattern.findall(ans)
                        if final_anses:
                            return final_anses[0]

                num_lst = self.get_pos_lst(sentence,'m')
                if len(num_lst) == 0:
                    pass
                else:
                    return num_lst[0]
            return ans_sentences[0] # 没有找到时间  返回排名最高的句子
        elif self.question_type == 'TIME':
            for sentence in ans_sentences:
                time_lst = self.get_pos_lst(sentence,'nt')
                if len(time_lst) == 0:
                    pass
                else:
                    return time_lst[0]
            return ans_sentences[0] # 没有找到时间  返回排名最高的句子
        elif self.question_type == 'NEXT_SENTENCE':
            type = self.get_context_type(ques)
            pattern1 = re.compile('“(.*?)”')
            pattern2 = re.compile('"(.*?)"')
            shici_sent_lst = pattern1.findall(ques)
            shici_sent_lst.extend(pattern2.findall(ques))
            shici_sent = shici_sent_lst[-1]
            # 寻找合适的答案
            for sent in ans_sentences:
                if sent.find(shici_sent) > -1:
                    ans = sent
                    break

            punc_lst = [',','.','?','，','。','？','!','！','「','」','"','“','”',"'","‘","’"]
            start_index = -1
            end_index = -1
            if type == '下文':
                index = ans.find(shici_sent)
                for i in range(index,len(ans)):
                    if ans[i] in punc_lst and start_index == -1:
                        start_index = i
                    elif ans[i] in punc_lst and end_index == -1:
                        end_index = i
                        break
                return ans[start_index+1:end_index]
            else:
                index = ans.find(shici_sent)
                start_index = -1
                end_index = -1
                for i in range(index,-1,-1):
                    if ans[i] in punc_lst:
                        end_index = i
                        break
                for i in range(end_index-1,-1,-1):
                    if ans[i] in punc_lst:
                        start_index = i
                        break
                return ans[start_index+1:end_index]
        elif self.question_type == 'COLOR':#对颜色进行提取
            ans_words = list(self.segmentor.segment(ans))
            ans_postags = list(self.postagger.postag(ans_words))
            final_anses = list()
            i = 0
            for tag in ans_postags:
                if tag == 'a' and ans_words[i].find("色") > -1 and len(ans_words[i]) > 1:
                    final_anses.append(ans_words[i])
                i = i + 1
            if final_anses:
                return '、'.join(final_anses)
            else:
                return ans
        elif self.question_type == 'AFFIRMATION': # 认同关系 是否
            tfidf = analyse.extract_tags
            kw_lst = tfidf(self.question)[0:5]
            score = 0
            for kw in kw_lst:
                if ans.find(kw) > -1:
                    score = score+1
            if score > len(kw_lst)/2 :
                return "是"
            else:
                return "否"
        else: #通用解决方法
            ans = ans_sentences[0] # 从候选答案集中选出一个句子
            ans_words = list(self.segmentor.segment(ans)) #ａｎｓ　的分词
            ans_postags = list(self.postagger.postag(ans_words)) # 词性标注
            ans_arcs = self.parser.parse(ans_words,ans_postags)
            # 问句进行分词
            # 有的问句没有类型  直接加一个‘什么’
            if (ques[-1] in ['?','？','.','。','!','！'] and ques[-2] == '是'):
                ques = ques[0:-1] + '什么' + ques[-1]
            elif ques[-1] == '是':
                ques = ques + '什么'
            que_words = list(self.segmentor.segment(ques))
            que_postags = list(self.postagger.postag(que_words))
            que_arcs = self.parser.parse(que_words,que_postags)


            # 找到ans_arcs中的head
            i = 0
            for arc in ans_arcs:
                if arc.relation == 'HED':
                    ans_core_word = ans_words[i]
                    ans_core_word_index = i + 1 # 依存关系从1开始   0是root
                    break
                i = i + 1
            ans_second_words = dict() # 依存关系树中 第二级词语
            i = 0
            for arc in ans_arcs:
                if arc.head == ans_core_word_index:
                    ans_second_words[ans_words[i]] = {'tag':ans_postags[i],'rea_index':i,'rel':arc.relation}
                i = i+1

            # 找到que_arcs中的head
            i = 0
            try:
                for arc in que_arcs:
                    if arc.relation == 'HED':
                        que_core_word = que_words[i]
                        que_core_word_index = i + 1  # 依存关系从1开始   0是root
                        break
                    i = i + 1
            except Exception as e:
                print(ans_words)
                print(i)
                print("\t".join("%d:%s" % (arc.head, arc.relation) for arc in que_arcs))
            que_second_words = dict()  # 依存关系树中 第二级词语
            i = 0
            for arc in que_arcs:
                if arc.head == que_core_word_index:
                    que_second_words[que_words[i]] = {'tag': que_postags[i], 'rea_index': i, 'rel': arc.relation}
                i = i + 1

            # 删除 非名词 在问题种出现的名词
            del_word_lst = list()
            for word,dic in ans_second_words.items():
                if ques.find(word) > -1 or dic['tag'] != 'n':
                    del_word_lst.append(word)
                    continue

            for word in del_word_lst:
                del ans_second_words[word]

            if len(ans_second_words) == 0:
                return ans
            elif len(ans_second_words) == 1:
                for word,dic in ans_second_words.items():
                    return  word

            # 依旧存在多个名词时
            question_word_list = ['谁','什么','哪一个','哪个','哪','多少']
            question_word = self.list_has_intersection(que_words,question_word_list) # 疑问词
            final_anses = ''
            if question_word == None: # 找不到 返回第一个词语
                for word,dic in ans_second_words.items():
                    final_anses = final_anses + word
                return final_anses

            if question_word in list(que_second_words.keys()):
                rel = que_second_words[question_word]['rel']
            else:
                rel = self.get_core_rel(que_arcs,que_words,question_word)

            for word,dic in ans_second_words.items():
                if dic['rel'] == rel:
                    return word
            # 没有找到一样的 返回第一个吧
            for word,dic in ans_second_words.items():
                final_anses = final_anses + word
            return final_anses






    
    # 计算候选答案句与问句的相似度，并返回排序后相似度最高的五个句子
    def sort_sentences(self):
        # 首先得到问句的c&r词集
        question_cr_words = self.get_centrial_and_rela_words(self.question)
        sims = []
        i = 0
        for sentence in self.sentences:
            sim = 0.1*self.calc_similarity(sentence, self.question) + 0.9*self.cal_sim(sentence, self.question) #!!!  这里修改了  相似度算法
            sims.append((i, sim))
            i = i+1
        sims.sort(key = lambda item:item[1], reverse = True)
        # print(sims)
        ans_sentences = []
        for i in range(0, 5):
            ans_sentences.append(self.sentences[sims[i][0]])
        return ans_sentences
    
    # 句法分析，得到一个句子的核心词和依附于核心词的词的集合
    def get_centrial_and_rela_words(self, sentence):
        words = self.segmentor.segment(sentence) # 分词
        # print(' '.join(words))
        postags = self.postagger.postag(words) # 词性标注
        # print(' '.join(postags))
        arcs = self.parser.parse(words, postags) # 句法分析
        i = 1 # 临时变量，指示句法树当前结点
        layer_2 = [] # 句法树第二层结点索引
        layer_3 = [] # 句法树第三层结点索引
        for arc in arcs:
            # print("%d<--%d:%s" % (i, arc.head, arc.relation))
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
        # 除了第一个词，后面把第二第三层的词算作依附于核心词的相关词
        for j in layer_2:
            rela_words.append(words[j-1])
        for j in layer_3:
            rela_words.append(words[j-1])
        return rela_words
    
    # 计算两个词语的语义距离
    # Dist(A,B) = min{dist(m,n)}
    # dist(m,n) = 2 * (7 - first_diff)
    # first_diff是两个词的code的第一个不同字符所在的位置
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




    def cal_sim(self,sentence,ques):
        '''
        计算相似度
        :param sentence:
        :param question_cr_words:
        :return:
        '''
        tfidf = analyse.extract_tags
        ques_keywords = tfidf(ques)
        score = 0
        for kw in ques_keywords:
            if sentence.find(kw) > -1:
                score = score + 1
        return score

    # 计算某句子与问句的相似度
    # 对于认不出来的词（同义词词林中没有）
    # 有很大可能是专有名词等，这时都识别为 “谜、谜语”即可
    # 专有名词于是被认为是相似的，我觉得这个是有道理的
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

# 现在生成答案提取器之后，调用do_ans_extract复用即可
ans_extractor = AnsExtractor()
# # 测试1
# test_sentences = ["《资治通鉴》是我国古代著名史学家、政治家司马光和他的助手刘攽、刘恕、范祖禹、司马康等人历时十九年编纂的一部规模空前的编年体通史巨著",
#                   "《资治通鉴》（常简作《通鉴》）是由北宋司马光主编的一部多卷本编年体史书",
#                   "《资治通鉴》是司马光及其助刘攽、刘怒、范祖禹等根据大量的史料编纂而成的一部编年体史书",
#                   "《资治通鉴》是由北宋司马光主编的一部多卷本编年体史书",
#                   "史记的作者是司马迁",
#                   "《论语》这类书比作教材中的公式概念,把《资治通鉴》比作试题",
#                   "想买一套《史记》和《资治通鉴》,求推荐版本",
#                   " 姜鹏品读《资治通鉴》"]
# answer = ans_extractor.do_ans_extract(test_sentences, "", "人物", "《资治通鉴》的作者是谁？",
#                                       0.8, 0.2)
# print(answer)
#
# # 测试2
# test_sentences = ["木婉清的母亲秦红棉被段正淳负心后伤心欲绝",
#                   "《天龙八部》中段誉和木婉清的爱情故事",
#                   "木婉清,金庸武侠小说《天龙八部》中的人物",
#                   "天龙八部(世纪新修版)书中最后一段介绍了木婉清被册封为贵妃。",
#                   "木婉清同父异母的姐姐是王语嫣",
#                   "木婉清的个性里沿袭了一部分母亲的执着和父亲的多情",
#                   "《天龙八部》中木婉清的饰演者有很多,最近的就有赵圆瑗、蒋欣等",
#                   "秦红棉，金庸武侠小说《天龙八部》中的人物，外号修罗刀,是木婉清的母亲"]
# answer = ans_extractor.do_ans_extract(test_sentences, "", "人物", "金庸小说《天龙八部》中，木婉清的母亲是谁?",
#                                       0.8, 0.2)
# print(answer)
# 测试3
# test_sentences = ["根据1939年签署的苏德互不侵犯条约，该市被划入罗马尼亚管治",
#                   "这一示威是为了希望世界能够关心三国共同的历史遭遇——在1939年8月23日苏联和纳粹德国秘密签订的《苏德互不侵犯条约 》中，该三国被苏联占领。",
#                   "苏德互不侵犯条约《苏德 互不侵犯条约》是1939年第二次世界大战爆发前苏联与纳粹德国在莫斯科所秘密签订之互不侵犯条约，目标是初步建立苏德在扩张之间的友谊与共识，并导致波兰被瓜分。",
#                   "最后 ， 双方 在 8 月 23 日 签订 德苏 互不侵犯条约.",
#                   " 8 月 17 日 ， 德驻 苏 大使 舒伦堡 再次 会见 莫洛托夫 ， 表示 愿 与 苏 缔结 一项 互不侵犯条约 。"
#                  ]
# answer = ans_extractor.do_ans_extract(test_sentences, "", "地名", "《苏德互不侵犯条约》的签订地点是",
#                                       0.8, 0.2)
# print(answer)