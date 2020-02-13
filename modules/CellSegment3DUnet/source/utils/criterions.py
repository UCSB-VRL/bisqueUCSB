import torch.nn.functional as F
import torch

def dice(output, target):
    #output = F.sigmoid(output[:, 0])
    #print 'output shape:',output.shape
    #print 'target shape:',target.shape
    eps = 0.1
    num = 2*(output*target).sum()+eps # f1 score
    den = output.sum()+target.sum()+eps
    #print "dice %.5f"%(num/den)
    return 1.0 - num/den

def dice_loss(output,target):
    loss = 0
    #loss = F.cross_entropy(output,target)
    output = F.softmax(output,dim=1)
    for c in range (0,2):
        o = output[:,c]
        #print "output shape" +str(o.shape)
        t = (target==c).float()
        #print "target shape"+str(t.shape)
        loss+=0.25*dice(o,t)
    return loss

def class_avg(output,target):
    loss = 0
    output =F.softmax(output,dim=1) 
    for c in range(0,2):
        o = output[:,c]
        t = (target==c).float()
        accu_m = t.sum()/target.sum()
        accu_b = (t.numel()-t.sum())/(target.numel()-target.sum())
        loss += (accu_m+accu_b)/2
    return loss

def crossentropy(output,target):
    output = F.sigmoid(output)
    cross = -torch.sum(target*torch.log(output))
    return cross


def mse_f1(output, targets):
    pred_m, pred_d = F.sigmoid(output[:, 0]), output[:, 1:]
    m, d, w = targets

    l1 = torch.mean(w.unsqueeze(1)*m.unsqueeze(1)*(pred_d - d)**2) # mse

    l2 = 1.0 - (2.0*(pred_m * m).sum() + 2.0)/(pred_m.sum() + m.sum() + 2.0) # f1 score

    return l1 + l2
