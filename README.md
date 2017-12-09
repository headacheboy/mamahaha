# mamahaha

## 答案提取器

### 用法
```
ans_extractor = AnsExtractor() # 这一步加载所有ltp的模型，加载同义词词林

test_sentences = ["木婉清的母亲秦红棉被段正淳负心后伤心欲绝",
                  "《天龙八部》中段誉和木婉清的爱情故事",
                  "木婉清,金庸武侠小说《天龙八部》中的人物",
                  "天龙八部(世纪新修版)书中最后一段介绍了木婉清被册封为贵妃。",
                  "木婉清同父异母的姐姐是王语嫣",
                  "木婉清的个性里沿袭了一部分母亲的执着和父亲的多情",
                  "《天龙八部》中木婉清的饰演者有很多,最近的就有赵圆瑗、蒋欣等",
                  "秦红棉，金庸武侠小说《天龙八部》中的人物，外号修罗刀,是木婉清的母亲"]
test_key_words = ["木婉清", "天龙八部", "母亲"]
test_question_type = "人物"
test_question = "金庸小说《天龙八部》中，木婉清的母亲是谁?"
test_a = 0.8
test_b = 0.2

# 这一步针对一组特定的问题、句子进行答案抽取
answer = ans_extractor.do_ans_extract(test_sentences,
    test_key_words, test_question_type, test_question,
    test_a, test_b)
print(answer)
```

### 主要函数说明
1.\__init\__(self)：
    这个函数构建答案提取器对象AnsExtractor，只负责加载ltp模型和同义词词林（或许还需要加载中文停用词表）
    
2.get_sim_cloud(self):
    读取同义词词林，得到的是一个dict，key是词，value是这个词的所有code
    
3.do_ans_extract(self, sents, key_words, ques_type, ques, a, b):
    执行答案抽取，主流程函数
    这个函数首先初始化几个参数
    然后调用self.sort_sentences()
    得到五个最可能包含答案的句子后（***#Has Done***）。
    对这5个句子需要做答案抽取处理（***#TODO***)
    
    个人认为答案抽取，需要使用关键词（看看答案句中关键词出现的怎么样）、问题类型（根据不同的问题类型，识别不同的命名实体，把识别出的命名实体作为最终的答案）

4.sort_sentences(self):
    计算候选答案句与问句的相似度，并返回排序后相似度最高的五个句子
    以下的几个函数都服务于这个函数
    
5.get_centrial_and_rela_words(self, sentence):
    工具函数。
    句法分析，得到一个句子的核心词和依附于核心词的词的集合。
    对问句和所有可能答案句都会执行一次。
    返回结果中，第一个元素是核心词，其他的是第二第三层相关词。
    
6.calc_Dist(self, codes1, codes2):
    工具函数。
    计算两个词语的语义距离。传进来的是两个词的code集合。
    
7.calc_similarity(self, sentence, question_cr_words):
    计算某句子与问句的相似度。
    这里具体实现了句子相似度算法。

    
### 函数调用流程
现在各个函数之间没啥耦合关系了，各自基本上可以独立工作，或者管道式工作

do_ans_extract --> sort_sentences
___
sort_sentences --> get_centrial_and_rela_words(self.question)

sort_sentences --> get_centrial_and_rela_words(sentence in  self.sentences)

sort_sentences --> calc_similarity

sort_sentences --> sort
___
calc_similarity --> get_centrial_and_rela_words(sentence)

calc_similarity --> calc_Dist






  
