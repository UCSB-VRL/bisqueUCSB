import numpy as np


def Precision(outputs,targets):
    num_sample = len(outputs)
    precision=0
    for i in range(num_sample):
        output = outputs[i]
        output = output.argmax(0)
        #print output.shape
        target = targets[i]
        target = target[0,:,:,:]
        #print target.shape
        tp =  sum(sum(sum(output*target)))/output.size
        fp = sum(sum(sum(output*(1-target))))/output.size
        prec = tp/(tp+fp)
        precision+=prec
    return precision/num_sample

def Recall(outputs,targets):
    num_sample = len(outputs)
    recall=0
    for i in range(num_sample):
        output = outputs[i]
        output = output.argmax(0)
        target = targets[i]
        target = target[0,:,:,:]
        tp =  sum(sum(sum(output*target)))/output.size
        fn = sum(sum(sum((1-output)*target)))/output.size
        rec = tp/(tp+fn)
        recall+=rec
    return recall/num_sample

def F1_score(outputs,targets):
    precision = Precision(outputs,targets)
    recall = Recall(outputs,targets)
    return 2*precision*recall/(precision+recall)