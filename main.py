from AnsExtractor import *


def get_train_ans(ques_path,ques_type_path,ans_path):
    '''
    得到最终答案
    :param ques_path: 问题文件路径
    :param ques_type_path:  问题类型文件路径
    :param ans_path:   候选答案文件路径
    :return:  生成最后答案
    '''
    ae = AnsExtractor()
    ques_file = open(ques_path,"r",encoding="utf-8")
    ques_type_file = open(ques_type_path,"r",encoding="utf-8")
    ans_file = open(ans_path,"r",encoding="utf-8")
    out_file = open("answers.txt","w",encoding="utf-8")
    i = 0
    for ques_line in ques_file:
        ques_line = ques_line.strip()
        lst = ques_line.split("\t")
        question = lst[0]
        type = ques_type_file.readline()
        type = type.strip()
        ans_lst = list()

        ans_line = ans_file.readline().strip()
        ans_line = ans_file.readline().strip()
        while ans_line != "":
            ans_lst.append(ans_line)
            ans_line = ans_file.readline().strip()
            # print(ans_line)
        ans_line = ans_file.readline().strip()

        # 输出答案
        answer = ae.do_ans_extract(ans_lst,"",type,question,0.1,0.9)
        # out_file.write(str(i) + "\n")
        i = i + 1
        # out_file.write(question + "\n")
        # out_file.write(type + "\n")
        # out_file.write(str(ans_lst) + "\n")
        out_file.write(str(answer)+"\n")

    ques_type_file.close()
    ans_file.close()
    ques_file.close()
    out_file.close()



if __name__ == '__main__':
    get_train_ans("wdm_assignment_3_samples.txt","200questiontype","200ans.txt")
