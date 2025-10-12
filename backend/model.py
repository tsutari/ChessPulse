import torch.nn as nn, torch

class TinyPolicyNet(nn.Module):
    def __init__(self,out_dim=4672):
        super().__init__()
        self.net=nn.Sequential(
            nn.Conv2d(13,32,3,padding=1),nn.ReLU(),
            nn.Conv2d(32,64,3,padding=1),nn.ReLU(),
            nn.AdaptiveAvgPool2d((4,4)),nn.Flatten(),
            nn.Linear(64*4*4,512),nn.ReLU(),
            nn.Linear(512,out_dim)
        )
    def forward(self,x): return self.net(x)

