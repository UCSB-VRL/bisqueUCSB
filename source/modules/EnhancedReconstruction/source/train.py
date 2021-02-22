import argparse

import torch
import numpy as np
from torch import nn, optim
from torch.utils.data import DataLoader

from torchvision import datasets, transforms, utils

from tqdm import tqdm

from source.model import DQLR
from scheduler import CycleScheduler
from dataloader import VideoDataset

def train(epoch, loader, model, optimizer, scheduler):
    loader = tqdm(loader)

    criterion = nn.MSELoss()

    latent_loss_weight = 0.25
    sample_size = 6

    mse_sum = 0
    mse_n = 0
    model.train()

    for i, (img, img_s) in enumerate(loader):
        model.zero_grad()

        img = img.cuda() #.to(device)
        img_s = img_s.cuda()
        #print(img_s.shape)
        out, latent_loss = model(img)
        recon_loss = 0.0
        #print(len(out))
        #print(out.shape)
        for j in range(len(out)):
            recon_loss += criterion(out[j], img_s[:,j,:,:])
        recon_loss /= 3.0
        latent_loss = latent_loss.mean()
        loss = recon_loss + latent_loss_weight * latent_loss
        loss.backward()

        if scheduler is not None:
            scheduler.step()
        optimizer.step()

        mse_sum += recon_loss.item() * img.shape[0]
        mse_n += img.shape[0]

        lr = optimizer.param_groups[0]['lr']

        loader.set_description(
            (
                f'epoch: {epoch + 1}; mse: {recon_loss.item():.5f}; '
                f'latent: {latent_loss.item():.3f}; avg mse: {mse_sum / mse_n:.5f}; '
                f'lr: {lr:.5f}'
            )
        )

        if i % 250 == 0:
            model.eval()

            sample = img[:sample_size]

            with torch.no_grad():
                out, _ = model(sample)
            

            sample = img_s[:sample_size,2,:,:,:].reshape(-1,3,256,256)
            #sample = sample.div(255)
            #out[2] = out[2].div(255)
 
            utils.save_image(
                torch.cat([sample, out[2]], 0),
                f'./sample/{str(epoch + 1).zfill(5)}_{str(i).zfill(5)}.png',
                nrow=sample_size,
                normalize=True,
                range=(-1, 1),
            )
            model.train()

def evaluate(test_loader, model):
    model.eval()
    test_loader = tqdm(test_loader)

    criterion = nn.MSELoss()

    latent_loss_weight = 0.25
    sample_size = 6

    mse_sum = 0
    mse_n = 0
    with torch.no_grad():
        
        for i, (img, img_s) in enumerate(test_loader):
            img = img.cuda() #.to(device)
            img_s = img_s.cuda()
    
            out, latent_loss = model(img)
            recon_loss = 0.0
            for j in range(len(out)):
                recon_loss += criterion(out[j], img_s[:,j,:,:])
            recon_loss /= 3.0
            latent_loss = latent_loss.mean()
            loss = recon_loss + latent_loss_weight * latent_loss
            
            mse_sum += recon_loss.item() * img.shape[0]
            mse_n += img.shape[0]

            test_loader.set_description(
                (
                    f'Evaluating; mse: {recon_loss.item():.5f}; '
                    f'latent: {latent_loss.item():.3f}; avg mse: {mse_sum / mse_n:.5f}; '
                )
            )
    model.train()
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--size', type=int, default=256)
    parser.add_argument('--epoch', type=int, default=5600)
    parser.add_argument('--lr', type=float, default=3e-4)
    parser.add_argument('--sched', type=str)
    parser.add_argument('--pretrained', type=str)
    parser.add_argument('--ckp', type=str)
    parser.add_argument('--bs', type=int, default=32)
    parser.add_argument('path', type=str)

    args = parser.parse_args()

    print(args)

    device = 'cuda:0'

    transform = transforms.Compose(
        [
            transforms.Resize(args.size),
            transforms.CenterCrop(args.size),
            transforms.ToTensor(),
            transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5]),
        ]
    )

    #dataset = datasets.ImageFolder(args.path, transform=transform)
    #loader = DataLoader(dataset, batch_size=128, shuffle=True, num_workers=4)

    train_data = VideoDataset(args.path, split='train', clip_len=3, preprocess=False,transform=transform)
    loader = DataLoader(train_data, batch_size=args.bs, shuffle=True, num_workers=4)
    
    test_data = VideoDataset(args.path, split='val', clip_len=3, clip_jump=1,preprocess=False,transform=transform)
    test_loader = DataLoader(test_data, batch_size=args.bs, shuffle=True, num_workers=4)
    #raw_input('Enter')
    model = DQLR()
    if not args.pretrained == None:
        print('Loading pretrained weights...')
        pre_w = torch.load(args.pretrained)
        for key in pre_w.keys():
            model.state_dict()[key] = pre_w[key]
            if 'dec' in key: 
                key2 = key.replace('dec','dec1')
                model.state_dict()[key2] = pre_w[key]
                key2 = key.replace('dec','dec2')
                model.state_dict()[key2] = pre_w[key]
            if 'upsample_t' in key:
                key2 = key.replace('upsample_t','upsample_t1')
                model.state_dict()[key2] = pre_w[key]
                key2 = key.replace('upsample_t','upsample_t2')
                model.state_dict()[key2] = pre_w[key]
    else:
        print('Training from scratch')

    model = nn.DataParallel(model).cuda()

    optimizer = optim.Adam(model.parameters(), lr=args.lr)
    scheduler = None
    if args.sched == 'cycle':
        scheduler = CycleScheduler(
            optimizer, args.lr, n_iter=len(loader) * args.epoch, momentum=None
        )

    for i in range(args.epoch):
        train(i, loader, model, optimizer, scheduler)
        torch.save(
            model.module.state_dict(), f'{args.ckp}/vqvae_{str(i + 1).zfill(3)}.pt'
        )
        evaluate(test_loader, model)
