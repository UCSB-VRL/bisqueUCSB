import argparse
import os
import numpy as np
import tifffile
import json
import torch
from torchvision import transforms, utils
from tqdm import tqdm
from source.model import DQLR
from PIL import Image, ImageEnhance


def main(data_path, output_dir, jump, pretrained_path, force):

    transform = transforms.Compose(
        [
            # transforms.ToPILImage(),
            transforms.Resize(256),
            transforms.CenterCrop(256),
            transforms.ToTensor(),
            transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5]),
        ]
    )

    transform_out = transforms.Compose(
        [
            transforms.Normalize([-1, -1, -1], [2, 2, 2]),
            transforms.ToPILImage(),
            transforms.Resize(512),
            transforms.Grayscale(),
        ]
    )

    model = DQLR()

    try:
        model.load_state_dict(torch.load(pretrained_path))
        device = torch.device("cuda:0")
        model = model.to(device)
        
        print('Loaded model on GPU.')
    except:
        model.load_state_dict(torch.load(pretrained_path, map_location='cpu'))
        device = torch.device("cpu")
        print('Loaded model on CPU.')

    print('Preparing data...')
    with tifffile.TiffFile(data_path) as tiff:
        imMeta = {}
        page = tiff.pages[0]
        tags = page.tags
        for tag in tags:
            imMeta[tag.name] = tag.value
        # imMeta = json.dumps(imMeta)

    data = tifffile.imread(data_path)
    num_slices, h, w = data.shape
    print('Data prepared.')

    enhanced_data = np.zeros((num_slices, 3, h, w))
    enhanced_count = np.zeros(num_slices)

    with torch.no_grad():
        model.eval()
        for t_idx in tqdm(range(num_slices), desc="Processing stack"):
            img = transform(Image.fromarray(data[t_idx]).convert('RGB'))
            img = img.to(device)
            output_images, _ = model(img.unsqueeze_(0))

            # output_images = output_images.detach().cpu().numpy()
            slices_idx = [t_idx, t_idx + jump, t_idx + 2*jump]
            for o_idx, s_idx in enumerate(slices_idx):
                if s_idx < num_slices:
                    enhanced_data[s_idx] += invTransform(output_images[o_idx], transform_out)
                    enhanced_count[s_idx] += 1

        for t_idx in range(len(enhanced_count)):
            enhanced_data[t_idx] /= enhanced_count[t_idx]

        # enhanced_data += 0.5
        # enhanced_data *= 0.5

        filename = data_path.split('/')[-1]
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        outputFile = os.path.join(output_dir, filename.split('.')[0] + '_enhanced.tif')
        print("Output Stored at:", outputFile)
        enhanced_data = np.expand_dims(enhanced_data[:,0,...],0)
        tifffile.imsave(outputFile, enhanced_data.astype(np.uint16), metadata=imMeta)
        return outputFile


def invTransform(img, transform_out):
    img = img.squeeze().detach().cpu()
    img = transform_out(img)
    img = ImageEnhance.Sharpness(img).enhance(10)
    img = ImageEnhance.Contrast(img).enhance(0.95)
    # img = np.array(img)
    return img


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default='./data')
    parser.add_argument('--output', type=str, default='./outputs/default')
    parser.add_argument('--jump', type=int, default=1)
    parser.add_argument('--force', action='store_true')
    parser.add_argument('--pretrained', type=str, default='./checkpoints/model.pt')
    args = parser.parse_args()

    print(args)
    output = main(args.data, args.output, args.jump, args.pretrained, args.force)

