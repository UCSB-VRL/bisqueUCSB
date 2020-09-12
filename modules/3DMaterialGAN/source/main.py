import torch
from torch.utils.data import DataLoader
#from utils import ShapeNetDataset
from utils import grain_dataset
from argparser import Argparser
from train import training_loop, initialize_model, save_model
import os


def main():
    """
    Entry point for training
    Load dataset according to args and train model
    """
    
    args = Argparser().args
    torch.backends.cudnn.benchmark = True
    #os.environ["CUDA_VISIBLE_DEVICES"] = ','.join(str(x) for x in args.gpu)
    import pdb; pdb.set_trace()
    #data_path = f'./{args.input_dir}/{args.data_dir}/'
    data_path = f'/{args.input_dir}'
    #dataset = ShapeNetDataset(data_path)
    
    dataset = grain_dataset(data_path)
    data_loader = DataLoader(dataset=dataset, batch_size=args.batch_size,
                             num_workers=torch.cuda.device_count()*2,
                             shuffle=True, drop_last=True)
    #d_path = f'./{args.models_path}/{args.obj}_d_1600.tar'
    #g_path = f'./{args.models_path}/{args.obj}_g_1600.tar'
    
    d_path = None
    g_path = None
    
    d_model, g_model, d_optim, g_optim = initialize_model(args, d_path, g_path)

    # Always save model if something goes wrong, disconnects or what not
    try:
        gan = '' if args.unpac else 'Pac'
        two = '' if args.unpac else '2'
        #print(f'Training {gan}{args.gan_type.upper()}{two} on {args.device.upper()}')
        training_loop(data_loader, d_model, g_model, d_optim, g_optim, args)
    finally:
        save_model(args.models_path, d_path, g_path,
                   d_model, g_model, d_optim, g_optim, args)




if __name__ == '__main__':
    main()
