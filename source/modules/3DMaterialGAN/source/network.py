import torch
import  torch.nn as  nn
from torch.nn import init
from torch.nn import functional as F
from torch.autograd import Function

from math import sqrt

import random

class EqualLR:
    def __init__(self, name):
        self.name = name

    def compute_weight(self, module):
        weight = getattr(module, self.name + '_orig')
        fan_in = weight.data.size(1) * weight.data[0][0].numel()

        return weight * sqrt(2 / fan_in)

    @staticmethod
    def apply(module, name):
        fn = EqualLR(name)

        weight = getattr(module, name)
        del module._parameters[name]
        module.register_parameter(name + '_orig', nn.Parameter(weight.data))
        module.register_forward_pre_hook(fn)

        return fn

    def __call__(self, module, input):
        weight = self.compute_weight(module)
        setattr(module, self.name, weight)


def equal_lr(module, name='weight'):
    EqualLR.apply(module, name)
    
    return module



class EqualLinear(nn.Module):
    def __init__(self, in_dim, out_dim):
       super().__init__()
     
       linear = nn.Linear(in_dim, out_dim)
       linear.weight.data.normal_()
       linear.bias.data.zero_()
 
       self.linear = equal_lr(linear)

    def forward(self, input):
       return self.linear(input)



class ConstantInput(nn.Module):
    def __init__(self, channel, size=4):
       super().__init__()
       
       self.input = nn.Parameter(torch.randn(1, channel, size, size, size))
       
    def forward(self, input):
       batch = input.shape[0]
       out = self.input.repeat(batch, 1, 1, 1, 1)
    
       return out

class AdaptiveInstanceNorm(nn.Module):
    def __init__(self, in_channel, style_dim):
       super().__init__()
   
       
       self.norm = nn.InstanceNorm3d(in_channel)
       self.style = EqualLinear(style_dim, in_channel * 2)
       
       self.style.linear.bias.data[:in_channel] = 1
       self.style.linear.bias.data[in_channel:] = 0
  
    def forward(self, input, style):
       #import pdb; pdb.set_trace()
       style = self.style(style).unsqueeze(2).unsqueeze(3)
       style =  style.unsqueeze_(-1)
       gamma, beta = style.chunk(2,1)
    
       out = self.norm(input)
       out = gamma * out + beta
    
       return out 

class EqualConv3d(nn.Module):
    def __init__(self, *args, **kwargs):
       super().__init__()
   
       conv = nn.Conv3d(*args, **kwargs) 
       self.conv = conv 
    def forward(self, input):
       return self.conv(input)

class EqualConv3dTranspose(nn.Module):
    def __init__(self, *args, **kwargs):
       super().__init__()
   
       conv = nn.ConvTranspose3d(*args, **kwargs)
       self.conv = conv
    def forward(self, input):
       return self.conv(input)


class StyledConvBlock(nn.Module):
    def __init__(
       self,
       in_channel,
       out_channel, 
       kernel_size_1=4,
       kernel_size_2=2,
       stride_1=2,
       stride_2=1,
       padding_1=1,
       padding_2=1, 
       style_dim=512, 
       initial=False,
       upsample=False, 
       fused=False,
       Last=False 

    ):
       super().__init__()
      
       if initial:
           self.conv1 = ConstantInput(in_channel)                     
        
       else:

           if Last == False:
                self.conv1 = nn.Sequential( 
                                    EqualConv3dTranspose(
                    in_channel, out_channel, kernel_size_1, stride_1, padding=padding_1
),                                  
                                    nn.BatchNorm3d(out_channel)
                                      
                               )
                            
           else:
                self.conv1 = nn.Sequential(
                                      EqualConv3dTranspose(
                   in_channel, out_channel, kernel_size_1, stride_1, padding=padding_1
                )
                ) 
       
       self.adain1 = AdaptiveInstanceNorm(out_channel, style_dim)

       if Last ==True:
                self.lrelu1  =  nn.Sigmoid()
       else:
                self.lrelu1 = nn.ReLU()  
                            


    def forward(self, input, style):
       #import pdb; pdb.set_trace()
       out = self.conv1(input)
       out = self.adain1(out, style)    
       out = self.lrelu1(out)

       return out


class Generator(nn.Module):
    def __init__(self, code_dim, fused=True):
       super().__init__()
      
       self.progression = nn.ModuleList(
         [
             StyledConvBlock(512, 512, 4, 3, 2, 1, 1, 1, initial=True),    # 4
             StyledConvBlock(512, 512, 4, 3, 2, 1, 1, 1, upsample=False),  # 8
             StyledConvBlock(512, 512, 4, 3, 2, 1, 1, 1, upsample=False),  # 16
             StyledConvBlock(512, 512, 4, 3, 2, 1, 1, 1, upsample=False),  # 32
             StyledConvBlock(512, 1, 4, 3, 2, 1, 1, 1, upsample=False, Last=True)   # 64

         ]
       )
  
     
    def forward(self, style, noise, step=0, alpha=-1, mixing_range=(-1, -1)):
       out =  noise
       #import pdb; pdb.set_trace()
       if len(style) <2:
           inject_index = [len(self.progression) + 1] 
  
       else:
           inject_index = random.sample(list(range(step)), len(style) -1 )
    
       crossover = 0
    
       for i, conv in enumerate(self.progression):
           if mixing_range == (-1, -1):
                if crossover < len(inject_index) and i > inject_index[crossover]:
                    crossover = min(crossover + 1, len(style))

                style_step = style[crossover]

           else:
                if mixing_range[0] <= i <= mixing_range[1]:
                    style_step = style[1]

                else:
                    style_step = style[0]

           if i > 0 and step > 0:
                out_prev = out
           #import pdb; pdb.set_trace()
           #print(i)     
           out = conv(out, style_step)

        
       #import pdb; pdb.set_trace()
       batch_size,_, cube_len,_, _ = out.shape
       out = torch.cat(torch.split(out, batch_size // 2, dim=0 ), 1).view(-1, 2, cube_len, cube_len, cube_len)
       #print("final_shape:", out.shape)
       return out      
         

class StyledGenerator(nn.Module):
    def __init__(self, code_dim=512, n_mpl=8):
       super().__init__()
       
       self.generator = Generator(code_dim)

      
       layers = []
       for i in range(n_mpl):
           layers.append(EqualLinear(code_dim, code_dim))
           layers.append(nn.LeakyReLU(0.2))

       self.style = nn.Sequential(*layers)

    def forward(
        self,
        input,
        noise=None,
        step=4, 
        alpha=-1,
        mean_style=None,
        style_weight=0,
        mixing_range=(-1, -1),   
   
    ):
       #import pdb; pdb.set_trace() 
       styles = []

       if type(input) not in (list, tuple):
           input = [input]

       for i in input:
           styles.append(self.style(i))

       batch = input[0].shape[0]

    
       if mean_style is not None:
           styles_norm = []

           for style in styles:
                styles_norm.append(mean_style + style_weight * (style - mean_style))

           styles = styles_norm
       size = 4 
       noise = torch.randn(batch, 1, size, size, size, device=input[0].device)

       #import pdb; pdb.set_trace()
       return self.generator(styles, noise, step, alpha, mixing_range=mixing_range)
    def mean_style(self, input):
        style = self.style(input).mean(0, keepdim=True)

        return style

class ConvBlock(nn.Module):
    def __init__(
       self,
       in_channel,
       out_channel,
       kernel_size,
       stride, 
       padding,
       kernel_size2=None,
       padding2=None,
       downsample=False,
       fused=False,
       Last = False
    ):
       super().__init__()

       pad1 = padding
       pad2 = padding

       kernel1 = kernel_size
    
    
       if Last==False:
           self.conv1 = nn.Sequential(
                                EqualConv3d(in_channel, out_channel, kernel1, stride, padding=pad1),
                                nn.LeakyReLU(0.2),  
                        )

       else:
          
           self.conv1 = nn.Sequential(
                                EqualConv3d(in_channel, out_channel, kernel1,  padding=pad1),
                                #nn.Sigmoid(),  
                        )
  
    def forward(self, input):
       out = self.conv1(input)
       return out
 
class Discriminator(nn.Module):
    def __init__(self, fused=False, from_rgb_activate=False):
        super().__init__()

        self.progression = nn.ModuleList(
            [
                ConvBlock(2, 64, 4, 2, 1, downsample=False),  
                ConvBlock(64, 128, 4, 2, 1, downsample=False),  
                ConvBlock(128, 256, 4, 2, 1, downsample=False),  
                ConvBlock(256, 512, 4, 2, 1, downsample=False),  
                ConvBlock(512, 1, 4, 2, 0, downsample=False, Last= True), 
              
            ]
        )


       

        self.n_layer = len(self.progression)

      

    def forward(self, input, step=0, alpha=-1):
        
        #import pdb; pdb.set_trace() 
        for index in range(self.n_layer):
            if index == 0:
                out = self.progression[index](input)
                
            else:
                out = self.progression[index](out)
            #print(index)
            #print(out.shape)
 
        #import pdb; pdb.set_trace()
        out = out.view(-1)
     

        return out             
 
