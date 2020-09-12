import os
import time
from torch import nn
import torch
from torch import optim
import torch.autograd as autograd
import tensorboardX as tb
from utils import generate_z
#from stylegan_3D import StyledGenerator, Discriminator
from network import StyledGenerator, Discriminator


def print_progress(start, epoch, batch, d_acc, g_loss, data_len, args):
    """
    Print progress as <Epoch/Epochs, Data_len/Batch_size, Elapsed, g_loss, d_acc (if apparent)>
    """
    elapsed = time.time() - start

    output = f'Epoch {(epoch + 1)}/{args.epochs}, ' + \
        f'Batch {(batch + 1)}/{(data_len/args.batch_size)}, ' + \
        f'Elapsed: {elapsed:.2f}s, ' + \
        f'G_loss: {g_loss:.2f}'
    if args.gan_type in ['dcgan']:
        output += f', D_acc: {d_acc:.2f}'

    # Logging when in e.g. tmux
    f = open("output.txt", "a")
    f.write(f'{output}\n')
    f.close()
   
    print(output)


def initialize_generator(args):
    """
    Initializes a saved generator - used in testing
    """
    #g = Generator(args)
    g_model = StyledGenerator()
 
    g_model = nn.DataParallel(g_model)
    #import pdb; pdb.set_trace() 
    print(f'Loading generator from{args.test_path}')
    g_checkpoint = torch.load(args.test_path, map_location=args.device)
    g_model.load_state_dict(g_checkpoint['model_state_dict'])

    #g_model.to(args.device)
    g_model
    return g_model


def initialize_model(args, d_path, g_path):
    """
    Initializes models and optimizers.
    If model_paths is given, state_dicts for the
    models and the optimizers are loaded in.
    If the a device is given, models will be moved to the given
    device. Models will always be wrapped in `nn.DataParallel` for
    consistency when loading models across devices. This can however
    be a slowdown when running in single device environments.
    """
    #import pdb; pdb.set_trace()
    d = Discriminator()
    g = StyledGenerator()
    
    #d_model = nn.DataParallel(d).to(args.device)
    d_model = nn.DataParallel(d)
    #g_model = nn.DataParallel(g).to(args.device) 
    g_model = nn.DataParallel(g) 
    d_model = d_model.cuda()
    g_model = g_model.cuda()
    d_optim = optim.Adam(d_model.parameters(), betas=args.betas, lr=args.d_lr)
    g_optim = optim.Adam(g_model.parameters(), betas=args.betas, lr=args.g_lr)

    if d_path is not None and os.path.isfile(d_path) and g_path is not None and os.path.isfile(g_path):
        print(f'Loading discriminator from{d_path}')
        print(f'Loading generator from{g_path}')
        d_checkpoint = torch.load(d_path, map_location=args.device)
        g_checkpoint = torch.load(g_path, map_location=args.device)
        d_model.load_state_dict(d_checkpoint['model_state_dict'])
        g_model.load_state_dict(g_checkpoint['model_state_dict'])
        d_optim.load_state_dict(d_checkpoint['optimizer_state_dict'])
        g_optim.load_state_dict(g_checkpoint['optimizer_state_dict'])
        args.current_epoch = d_checkpoint['epoch']
        args.current_iteration = d_checkpoint['iteration']

    return d_model, g_model, d_optim, g_optim


def training_loop(data_loader, d_model, g_model, d_optim, g_optim, args):
    """
    Main training loop for all GANs
    """
    if args.gan_type in ['wgan-gp']:
        loss_function = None
    else:
        loss_function = nn.BCELoss().to(args.device)

    writer = tb.SummaryWriter(f'logs/{args.gan_type}_{args.data_dir}')
    start = time.time()
    batch_no = len(data_loader.dataset)/args.batch_size

    for epoch in range(args.current_epoch, args.epochs):
        print(f'Epoch {epoch + 1}/{args.epochs}')
        args.current_epoch = epoch
        g_train_it = epoch * batch_no

        for batch_idx, batch in enumerate(data_loader):
            g_train_it += 1
            #batch_idx = batch_idx.to(args.device)
            #import pdb; pdb.set_trace()
            batch = batch.cuda()
            d_acc, real_labels = d_train(
                d_model, g_model, d_optim, loss_function, batch, writer, args)
            g_loss = g_train(g_model, d_model, g_optim,
                             loss_function, real_labels, writer, args, g_train_it)
            print_progress(start, epoch, batch_idx, d_acc,
                           g_loss, len(data_loader.dataset), args)

        if epoch % args.save_freq is 0:
            d_save_path = f'./{args.models_path}/{args.obj}_d_{epoch}.tar'
            g_save_path = f'./{args.models_path}/{args.obj}_g_{epoch}.tar'
            models_path = f'./{args.models_path}'
            save_model(models_path, d_save_path, g_save_path,
                       d_model, g_model, d_optim, g_optim, args)


def d_train(d_model, g_model, d_optim, loss_function, batch, writer, args):
    """
    Training loop of discriminator
    """
    if args.labels == 'noisy':
        real_labels = (torch.FloatTensor(args.batch_size //
                                         (1 if args.unpac else 2)).uniform_(0.85, 1.0)).to(args.device)
        fake_labels = (torch.FloatTensor(args.batch_size //
                                         (1 if args.unpac else 2)).uniform_(0.0, 0.15)).to(args.device)
    elif args.labels == 'hard':
        real_labels = torch.ones(
            args.batch_size // (1 if args.unpac else 2)).to(args.device)
        fake_labels = torch.zeros(
            args.batch_size // (1 if args.unpac else 2)).to(args.device)
    elif args.labels == 'd_hard':
        real_labels = torch.FloatTensor([0.9 for _ in range(
            args.batch_size // (1 if args.unpac else 2))]).to(args.device)
        fake_labels = torch.zeros(
            args.batch_size // (1 if args.unpac else 2)).to(args.device)

    if not args.unpac:
        X = torch.cat(torch.split(batch, args.batch_size //
                                  2, dim=0), 1).view(-1, 2, args.cube_len, args.cube_len, args.cube_len)
        X = X.float().cuda()
    else:
        X = batch.view(-1, 1, args.cube_len, args.cube_len,
                       args.cube_len).to(args.device)

    d_total_acc = 0.0
    it = 0
    
    while it < args.d_iter and d_total_acc < args.d_low_thresh:
        args.current_iteration = args.current_iteration + 1
        #Z = generate_z(args).to(args.device)
        Z1, Z2 = generate_z(args)
        Z1 = Z1.float().cuda()
        Z2 = Z2.float().cuda()
        Z = [Z1, Z2]
        #import pdb; pdb.set_trace()
        d_real = d_model(X)
        if loss_function is None:
            d_real_loss = -torch.mean(d_real)
        else:
            d_real_loss = loss_function(d_real, real_labels)

        #import pdb; pdb.set_trace()
        if not args.unpac:
            fake = torch.cat(torch.split(
                g_model(Z), args.batch_size//2, dim=0), 1)
        else:
            fake = g_model(Z)
  
        #import pdb; pdb.set_trace()
        d_fake = d_model(fake)

        if loss_function is None:
            d_fake_loss = torch.mean(d_fake)
        else:
            d_fake_loss = loss_function(d_fake, fake_labels)

        if args.gan_type in ['wgan-gp']:
            grad_pen = calc_gradient_penalty(d_model, X, fake, args)
        else:
            grad_pen = 0.0

        d_loss = (d_fake_loss + d_real_loss) + grad_pen
 
        print(d_loss)

        if args.gan_type in ['wgan_gp']:
            writer.add_scalar('grad_pen', grad_pen, args.current_iteration)
        if args.gan_type in ['dcgan']:
            d_real_acc = torch.ge(d_real.squeeze(), 0.5).float()
            d_fake_acc = torch.le(d_fake.squeeze(), 0.5).float()
            d_total_acc = torch.mean(torch.cat((d_real_acc, d_fake_acc), 0))
            writer.add_scalar('d_total_acc', d_total_acc,
                              args.current_iteration)

        writer.add_scalar('d_real_loss', d_fake_loss, args.current_iteration)
        writer.add_scalar('d_fake_loss', d_fake_loss, args.current_iteration)
        writer.add_scalar('d_total_loss', d_fake_loss, args.current_iteration)

        if not (args.gan_type in ['dcgan'] and d_total_acc > args.d_high_thresh):
            d_optim.zero_grad()
            d_loss.backward()
            d_optim.step()

        summarize_grad(d_model, writer, args.current_iteration, 'd')
        it += 1

    return d_total_acc, real_labels

def g_train(g_model, d_model, g_optim, loss_function, real_labels, writer, args, git):
    """
    Training loop of generator
    """
    #Z = generate_z(args).to(args.device)
    Z1, Z2 = generate_z(args)
    Z1 = Z1.float().cuda()
    Z2 = Z2.float().cuda()
    Z = [Z1, Z2]
    if not args.unpac:
        fake = torch.cat(torch.split(g_model(Z), args.batch_size//2, dim=0), 1)
    else:
        fake = g_model(Z)
    d_fake = d_model(fake)

    if loss_function is None:
        g_loss = -torch.mean(d_fake)
    else:
        g_loss = loss_function(d_fake, real_labels)

    writer.add_scalar('g_loss', g_loss, git)

    g_optim.zero_grad()
    g_loss.backward()
    g_optim.step()
    summarize_grad(g_model, writer, git, 'g')

    return g_loss


def save_model(model_path, d_save_path, g_save_path, d_model, g_model, d_optim, g_optim, args):
    """
    Saves a model with epoch, iteration, model_state_dict and optimizer_state_dict
    """
    if not os.path.exists(model_path):
        os.mkdir(model_path)
    print(f'Saving discriminator to {d_save_path}')
    torch.save(
        {
            "epoch": args.current_epoch if args.current_epoch > -1 else 0,
            "iteration": args.current_iteration if args.current_iteration > -1 else 0,
            "model_state_dict": d_model.state_dict(),
            "optimizer_state_dict": d_optim.state_dict(),
            "hyperparameters": args
        },
        d_save_path
    )
    print(f'Saving generator to {g_save_path}')
    torch.save(
        {
            "epoch": args.current_epoch if args.current_epoch > -1 else 0,
            "iteration": args.current_iteration if args.current_iteration > -1 else 0,
            "model_state_dict": g_model.state_dict(),
            "optimizer_state_dict": g_optim.state_dict(),
            "hyperparameters": args
        },
        g_save_path
    )

    torch.cuda.empty_cache()

def calc_gradient_penalty(d_model, real_data, fake_data, args):
    """
    Calculates the gradient penalty
    """
    alpha = torch.rand((args.batch_size // (1 if args.unpac else 2), 1 if args.unpac else 2,
                        args.cube_len, args.cube_len, args.cube_len), requires_grad=True)

    alpha = alpha.float().cuda()
    interpolates = alpha * real_data + ((1 - alpha) * fake_data)

    disc_interpolates = d_model(interpolates)

    gradients = autograd.grad(outputs=disc_interpolates, inputs=interpolates,
                              grad_outputs=torch.ones(
                                  disc_interpolates.size()).cuda(),
                              create_graph=True, only_inputs=True)[0]

    gradients = gradients.view(real_data.size(0), -1)

    gradient_penalty = ((gradients.norm(2, dim=1) - 1)
                        ** 2).mean() * args.gp_lambda
    return gradient_penalty

def summarize_grad(model, writer, iteration, network_type):
    """
    Write the grads to the summary writeer
    """
    #for name, param in model.module.named_parameters():
    for name, param in model.named_parameters():

        if param.grad is not None:
            if name == 'layer1.0.weight':
                writer.add_scalar(f'{network_type}_1_grad',
                                  param.grad.norm().item(), iteration)
            elif name == 'layer2.0.weight':
                writer.add_scalar(f'{network_type}_2_grad',
                                  param.grad.norm().item(), iteration)
            elif name == 'layer3.0.weight':
                writer.add_scalar(f'{network_type}_3_grad',
                                  param.grad.norm().item(), iteration)
            elif name == 'layer4.0.weight':
                writer.add_scalar(f'{network_type}_4_grad',
                                  param.grad.norm().item(), iteration)
            elif name == 'layer5.0.weight':
                writer.add_scalar(f'{network_type}_5_grad',
                                  param.grad.norm().item(), iteration)

