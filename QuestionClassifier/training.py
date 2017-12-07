from sklearn import svm, neighbors, preprocessing
from sklearn.naive_bayes import MultinomialNB
from sklearn.externals import joblib
import re
import numpy as np

def nb(X, y):
    clf = MultinomialNB()
    clf.fit(X, y)
    return clf

def SVM(X, y, C, gamma):
    if C == None:
        C = 1.0
    if gamma == None:
        gamma = 1/X[0].shape[0]
    clf = svm.SVC(kernel='rbf', C=C, gamma=gamma, class_weight='balanced', probability=True)
    clf.fit(X, y)
    return clf

useful = ["r", "n", "a", "d", "v", "b", "t"]
#useful = ["r", "n"]
labelDic = {}
labelInd = 0
indLabel = {}

dic = {}
totalInd = 0

def loadLabel():
    global labelDic, labelInd, indLabel
    file = open("label", encoding='utf-8')
    for line in file:
        line = line.split()[0]
        if line not in labelDic:
            labelDic[line] = labelInd
            indLabel[labelInd] = line
            labelInd += 1
    #print(labelInd)

def getFeature(X, y, mode, file, fileLabel):
    global dic, totalInd
    before = 0
    for i in range(len(file)):
        if mode == 0:
            lineLabel = fileLabel[i]
            label = labelDic[lineLabel.split()[0]]
            y.append(label)
        line = file[i]
        line = line.replace("\n", "")
        line = line.replace("\r", "")
        ls = line.split('\t')
        tmp = np.zeros([11000])
        for num in ls:
            if num == ' /w':
                continue
            pos = num.rfind('/')
            word = num[:pos]
            tag = num[pos+1:]
            if len(tag) == 0 or tag[0] not in useful or tag == "vshi":
                continue
            elif tag[0] == "r":
                before = 1
            if mode == 0:
                if before == 1:
                    dic["1_"+word + "_" + tag] = totalInd
                    totalInd += 1
                    tmp[dic["1_"+word + "_" + tag]] += 1
                    before = 0
                    continue
                if word + "_" + tag not in dic:
                    dic[word + "_" + tag] = totalInd
                    totalInd += 1
                tmp[dic[word + "_" + tag]] += 1
                '''
                if tag not in dic:
                    dic[tag] = totalInd
                    totalInd += 1
                tmp[dic[word]] += 1
                tmp[dic[tag]] += 1
                '''
            else:
                if before == 1 and tag[0] in useful:
                    if "1_"+word + "_" + tag in dic:
                        tmp[dic["1_"+word + "_" + tag]] += 1
                        before = 0
                        continue
                if tag[0] in useful and word + "_" + tag in dic:
                    tmp[dic[word + "_" + tag]] += 1
                #if tag in dic:
                #    tmp[dic[tag]] += 1
            #print(word + "." + tag, end=' ')
        #tmp /= tmp.dot(tmp)
        X.append(tmp)
        #print(label)

if __name__ == "__main__":
    X = []
    y = []
    loadLabel()
    file = open("question", encoding='utf-8').readlines()
    fileLabel = open("label", encoding='utf-8').readlines()
    getFeature(X, y, 0, file, fileLabel)
    #print(totalInd)
    '''
    clf = nb(X, y)
    joblib.dump(clf, "model/model")
    fileDic = open("model/vocab", "w", encoding='utf-8')
    fileDic.write(str(dic))
    '''
    #'''
    dic = eval(open("model/vocab", encoding='utf-8').read())
    clf = joblib.load("model/model")
    #'''
    X.clear()
    y.clear()
    file = open("testing", encoding='utf-8').readlines()
    getFeature(X, None, 1, file, None)
    proba = clf.predict_proba(X)
    fileO = open("questionType", "w", encoding='utf-8')
    for ind, num in enumerate(clf.predict(X)):
        fileO.write(indLabel[num]+"\n")
        '''
        if max(proba[ind] > 0.3):
            print(indLabel[num])
        else:
            print("UNK")
        '''
