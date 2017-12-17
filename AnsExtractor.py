# -*- coding: utf-8 -*-

import re
import os
import pyltp
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import NamedEntityRecognizer
from pyltp import Parser
from pyltp import SementicRoleLabeller
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
    
    # init做的事情有：
    # 1、加载模型
    # 2、加载同义词词林
    # 3、加载补充的问题分类所需的规则数组
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
        # 以下是补充的问题分类所需的规则数组
        self.istime_lst = ['年份是',"时间是","哪一年","何时","什么时候","什么时间","哪一月","哪一日"]
        self.iscolor_lst = ['什么颜色',"哪种颜色","哪个颜色","颜色是"]
        self.unit_lst = ["回","对","山","只","刀","群","江","条","个","打","尾","手","双","张","溪","挑","坡","首","令","网","辆","座","阵","队",
                         "顶","匹","担","墙","壳","炮","场","扎","棵","支","颗","钟","单","曲","客","罗","岭","阙",
                         "捆","丘","腔","贯","袭","砣","窠","岁","倍","枚","次"]
        self.islocation_lst = ['哪个城市',"哪个国家",'国籍是',"什么国籍","哪个省","哪座城市", "县份是","地址在哪里","哪里","何处","何地","哪儿",
                               "什么地方","什么地点"]
        self.isorganization_lst = ['哪个组织',"组织是","哪个机构","什么组织","什么机构"]
        self.isperson_lst = ['哪个皇帝',"是谁","什么名字","者是","身份是","学家是","什么人","哪个人"]
        self.isnum_lst = list()
        for unit in self.unit_lst:
            self.isnum_lst.append("多少"+unit)
        self.stop_words = [] # 停用词目前还没用到
        self.sim_word_code = {} # 每个词有一个list，是它的编码（可能多个）
        self.get_sim_cloud()
        
    # 读取同义词词林
    def get_sim_cloud(self):
        """
        同义词词林中的词有三种关系，同义、相关（不一定同义）、独立词
        如果用于计算相似度的话，相关的词语具有相同的code，也是能接受的
        所以并没有区分词关系，而是直接读取了词的code
        填充sim_word_code
        """
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

    def get_index_list(self,str,word):
        '''
        获得word在str中的index列表
        :param str:
        :param word:
        :return: 返回一个列表  没有返回空列表
        '''
        start = 0
        lst = list()
        while start < len(str):
            index = str.find(word,start)
            if index == -1:
                break
            else:
                lst.append(index)
                start = index + 1
        return lst

    def cal_dis_with_dict(self,ques_kw_dic,ans_kw_dic):
        '''
        计算 问题关键词index 和 答案关键词index 之间的距离
        :param ques_kw_dic:
        :param ans_ke_dic:
        :return: 按照距离从小到大的 tuple组成的list
        '''
        result_dic = dict()
        for ans_kw,ans_kw_index_lst in ans_kw_dic.items():
            temp = 99999
            for ans_kw_index in ans_kw_index_lst:
                ans_kw_dis = 0
                for ques_kw,ques_kw_index_lst in ques_kw_dic.items():
                    temp_dis = 9999
                    for ques_kw_index in ques_kw_index_lst:
                        if abs(ques_kw_index - ans_kw_index) < temp_dis:
                            temp_dis = abs(ques_kw_index - ans_kw_index)
                    ans_kw_dis += temp_dis
                if ans_kw_dis < temp:
                    temp = ans_kw_dis
            result_dic[ans_kw] = temp
        # 排序 从小到大
        result_tup = sorted(result_dic.items(),key = lambda item:item[1])
        return result_tup

    def calc_dis_ner_with_dict(self,ques_kw_dic,ner_lst,ans):
        '''
        实体集合 计算距离问题关键词最近的
        :param ques_kw_dic:
        :param ner_lst:
        :param ans:
        :return: 返回 tuple组成的lst
        '''
        ner_dic = dict()
        for ner in ner_lst:
            temp = self.get_index_list(ans,ner)
            if temp:
                ner_dic[ner] = temp
        return self.cal_dis_with_dict(ques_kw_dic,ner_dic)

    def get_final_result(self,result_lst):
        '''
        对最终返回结果进行包装，若没有结果，返回"未找到准确答案"
        '''
        if len(result_lst) > 0:
            return result_lst[0][0]
        else:
            return "未找到准确答案"

    def gen_short_ans(self,ques_kw_lst,ans):
        '''
        对于超过 20字的答案 进行截断
        :param ques_kw_lst:
        :param ans:
        :return: 返回答案
        '''
        if len(ans) <= 20:
            return ans
        pattern = r"[，,。\.！!？\?]"
        lst = re.split(pattern, ans)
        result_dic = dict()
        for senten in lst:
            score = 0
            for kw in ques_kw_lst:
                if senten.find(kw) > -1:
                    score += 1
            result_dic[senten] = score
        result_dic = sorted(result_dic.items(),key=lambda item:item[1],reverse=True)
        if len(result_dic) > 0:
            return result_dic[0][0][0:20]
        else:
            return "未找到精确答案"

    def do_ans_extract(self, sents, key_words, ques_type, ques, a, b):
        '''
        调用答案抽取算法，这是主流程函数，返回即为答案
        :params: 这几个参数有候选答案句集合、关键词集合（没有用到）、问题种类、问句、算法参数
        :return:返回最终的答案
            返回的答案大多是一个词，如果不能返回一个词
            那么返回一个长度不超过20个字的句子
            如果句子和词都找不到
                返回"未找到准确答案"
            如果没有得到合适的候选答案句集合
                返回"没有找到相关内容"
        '''
        self.sentences = sents # 候选答案句集合
        self.key_words = key_words # 关键词集合
        self.question_type = ques_type # 问题种类
        self.question = ques # 问句
        self.a = a
        self.b = b # 句法相似度计算算法的两个参数
        tfidf = analyse.extract_tags

        # 问题 关键词 位置
        ques_kw_lst = tfidf(ques)
        ques_kw_dic = dict()
        for kw in ques_kw_lst:
            lst = self.get_index_list(ques, kw)
            if lst:
                ques_kw_dic[kw] = lst
        # 补充的基于规则的问题分类
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
        elif self.has_spe_words(self.question, self.isorganization_lst):
            self.question_type = "ORGANIZATION"
            ques_type = "ORGANIZATION"

        # 去掉候选答案句中的空白字符
        for i in range(len(self.sentences)):
            self.sentences[i] = ''.join(self.sentences[i].split())
        # 首先得到最有可能包含答案的句子
        ans_sentences = self.sort_sentences() 
        
        # 然后根据问题类型，在这五个句子中进行答案抽取
        if len(ans_sentences) == 0:
            return "没有找到相关内容"
        # 取最可能包含答案的句子，进入下一步
        ans = ans_sentences[0]

        # 基于问题分类器的分类和规则补充的分类，采取不同的抽取策略
        if self.question_type == "PERSON":
            final_anses = self.get_all_NER(ans,'Nh')
            temp_lst = list()
            # 去除出现在问句中的人物实体
            for ner in final_anses:
                if ques.find(ner) == -1:
                    temp_lst.append(ner)
            final_anses = temp_lst
            if len(final_anses) == 0:
                return self.gen_short_ans(ques_kw_lst,ans)
            else:
                # 返回和问题关键词最接近的实体
                return self.get_final_result(self.calc_dis_ner_with_dict(ques_kw_dic,final_anses,ans))
        elif self.question_type == 'LOCATION':
            final_anses = self.get_all_NER(ans, 'Ns')
            temp_lst = list()
            for ner in final_anses:
                if ques.find(ner) == -1:
                    temp_lst.append(ner)
            final_anses = temp_lst
            if len(final_anses) == 0:
                return self.gen_short_ans(ques_kw_lst,ans)
            else:
                return self.get_final_result(self.calc_dis_ner_with_dict(ques_kw_dic,final_anses,ans))
        elif self.question_type == 'ORGANIZATION':
            final_anses = self.get_all_NER(ans, 'Ni')
            temp_lst = list()
            for ner in final_anses:
                if ques.find(ner) == -1:
                    temp_lst.append(ner)
            final_anses = temp_lst
            if len(final_anses) == 0:
                return self.gen_short_ans(ques_kw_lst,ans)
            else:
                return self.get_final_result(self.calc_dis_ner_with_dict(ques_kw_dic,final_anses,ans))
        elif self.question_type == 'NUMBER' :
            for sentence in ans_sentences:
                for num_word in self.isnum_lst:
                    if self.question.find(num_word) > -1:
                        pattern = re.compile("([\d|零|一|二|三|四|五|六|七|八|九|十|百|千|万|亿]+){unit}".format(unit=num_word[-1]))
                        final_anses = pattern.findall(ans)
                        if final_anses:
                            return self.get_final_result(self.calc_dis_ner_with_dict(ques_kw_dic,final_anses,ans))

                num_lst = self.get_pos_lst(sentence,'m')
                if len(num_lst) == 0:
                    return self.gen_short_ans(ques_kw_lst,ans)
                else:
                    return self.get_final_result(self.calc_dis_ner_with_dict(ques_kw_dic,num_lst,ans))
            return ans_sentences[0] # 没有找到 返回排名最高的句子，注：这句话没用
        elif self.question_type == 'TIME':
            for sentence in ans_sentences:
                time_lst = self.get_pos_lst(sentence,'nt')
                if len(time_lst) == 0:
                    return self.gen_short_ans(ques_kw_lst,ans)
                else:
                    return self.get_final_result(self.calc_dis_ner_with_dict(ques_kw_dic,time_lst,ans))
            return ans_sentences[0] # 没有找到  返回排名最高的句子,注：这句话没用
        elif self.question_type == 'NEXT_SENTENCE':
            type = self.get_context_type(ques)
            pattern1 = re.compile('“(.*?)”')
            pattern2 = re.compile('"(.*?)"')
            shici_sent_lst = pattern1.findall(ques)
            shici_sent_lst.extend(pattern2.findall(ques))
            if len(shici_sent_lst) == 0:
                return self.gen_short_ans(ques_kw_lst,ans)
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
                return ans[start_index+1:end_index][0:20]
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
                return ans[start_index+1:end_index][0:20]
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
                return self.gen_short_ans(ques_kw_lst,ans)
        elif self.question_type == 'AFFIRMATION': # 认同关系 是否
            kw_lst = tfidf(self.question)[0:5]
            score = 0
            for kw in kw_lst:
                if ans.find(kw) > -1:
                    score = score+1
            if score > len(kw_lst)/2 :
                return "是"
            else:
                return "否"
        else: #通用解决方法，针对一般类型的问题
            # 对问题和候选答案进行关键词提取
            ques_kw_lst = tfidf(ques)
            ans_kw_lst = tfidf(ans)

            # 去掉出现在问题的关键词
            temp_lst = list()
            for kw in ans_kw_lst:
                if ques.find(kw) == -1:
                    temp_lst.append(kw)
            ans_kw_lst = temp_lst

            # 对答案关键词 作词性标注，保留名词性质的词
            ans_kw_postags = self.postagger.postag(ans_kw_lst)
            temp_lst = list()
            index = 0
            for postag in ans_kw_postags:
                if postag in ['n', 'nd', 'nh', 'ni', 'nl', 'ns', 'nt', 'nz']:
                    temp_lst.append(ans_kw_lst[index])
                index = index + 1
            ans_kw_lst = temp_lst

            # 计算关键词的位置
            # 问题关键词
            ques_kw_dic = dict()
            for kw in ques_kw_lst:
                lst = self.get_index_list(ques,kw)
                if lst:
                    ques_kw_dic[kw] = lst
            # 答案关键词
            ans_kw_dic = dict()
            for kw in ans_kw_lst:
                lst = self.get_index_list(ans, kw)
                if lst:
                    ans_kw_dic[kw] = lst

            # 得到 距离排序后，最小的那一个词作为答案
            ans_dis = self.get_final_result(self.cal_dis_with_dict(ques_kw_dic,ans_kw_dic))
            return ans_dis
    
    # 计算候选答案句与问句的相似度，并返回按相似度排序的句子
    def sort_sentences(self):
        # 首先得到问句的c&r词集
        question_cr_words = self.get_centrial_and_rela_words(self.question)
        sims = []
        i = 0
        for sentence in self.sentences:
            try:
                sim = 0.1*self.calc_similarity(sentence, question_cr_words) + 0.9*self.cal_sim(sentence, self.question)
            except Exception as err:
                print(err)
                sim = self.cal_sim(sentence, self.question) # 相似度算法有可能发生除零错误
            sims.append((i, sim))
            i = i+1
        sims.sort(key = lambda item:item[1], reverse = True)
        ans_sentences = []
        for i in range(0, len(self.sentences)):
            ans_sentences.append(self.sentences[sims[i][0]])
        return ans_sentences
    
    # 句法分析，得到一个句子的核心词和依附于核心词的词的集合
    def get_centrial_and_rela_words(self, sentence):
        words = self.segmentor.segment(sentence) # 分词
        postags = self.postagger.postag(words) # 词性标注
        arcs = self.parser.parse(words, postags) # 句法分析
        i = 1 # 临时变量，指示句法树当前结点
        layer_2 = [] # 句法树第二层结点索引
        layer_3 = [] # 句法树第三层结点索引
        for arc in arcs:
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
            # 有点复杂，所以没实现这些规则。
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
        # 除了核心词，把第二第三层的词都算作依附于核心词
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
        计算相似度，基于关键词，不涉及句法
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
    # 专有名词于是被认为是相似的
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
