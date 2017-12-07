question和label是对应的query-type文件的训练集。在question的一行问句对应着label里同行的type。
若要增加训练集，将preprocess.py里file和file0给改掉。最上面两行语句是修改训练集的，最下面两行语句是修改测试集的。

#file = open("question_simplified", encoding='utf-8')
#fileO = open("question", "w", encoding='utf-8')
#file = open("input", encoding='utf-8')
#fileO = open("testing", "w", encoding='utf-8')

当前是使用已经训练好的模型。

input和testing。input是输入的测试集。需要使用preprocess.py将input转换为testing，然后才能调用training来运行。
使用了Hanlp。

输出在questionType中。