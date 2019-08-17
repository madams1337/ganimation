from torch.utils import data
from torchvision import transforms as T
from torchvision.datasets import ImageFolder
from PIL import Image
import torch
import os
import random
import numpy as np


class CelebA(data.Dataset):
    """Dataset class for the CelebA dataset."""
    def __init__(self, image_dir, attr_path, transform, mode, c_dim):
        """Initialize and preprocess the CelebA dataset."""

        self.image_dir = image_dir
        self.attr_path = attr_path
        self.transform = transform
        self.mode = mode
        self.c_dim = c_dim

        self.train_dataset = []
        self.test_dataset = []
        
        self.preprocess() # Fills train_dataset and test_dataset --> [filename, boolean attribute vector]

        if mode == 'train':
            self.num_images = len(self.train_dataset)
        else:
            self.num_images = len(self.test_dataset)
        
        print("------------------------------------------------")
        print("Training images: ", len(self.train_dataset))
        print("Testing images: ", len(self.test_dataset))


    def preprocess(self):
        """Preprocess the CelebA attribute file."""
        lines = [line.rstrip() for line in open(self.attr_path, 'r')]
        lines = lines[2:]
        
        random.seed(1234)
        random.shuffle(lines)

        # Extract the info from each line
        for i, line in enumerate(lines):
            split = line.split()
            filename = split[0]
            values = split[1:]
            label = [] # Vector representing the presence of each attribute in each image

            for n in range(self.c_dim):
                label.append(float(values[n])/5.)

         
            self.test_dataset.append([filename, label])
            break
        
        print('Dataset ready!...')


    def __getitem__(self, index):
        """Return one image and its corresponding attribute label."""
        dataset = self.train_dataset if self.mode == 'train' else self.test_dataset
        filename, label = dataset[index]
        image = Image.open(os.path.join(self.image_dir, filename))
        return self.transform(image), torch.FloatTensor(label)


    def __len__(self):
        """Return the number of images."""
        return self.num_images


def get_loader(image_dir, attr_path, c_dim, image_size=128, 
               batch_size=25, mode='train', num_workers=1):
    """Build and return a data loader."""
    transform = []
    transform.append(T.ToTensor())
    transform.append(T.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5)))
    transform = T.Compose(transform)

    dataset = CelebA(image_dir, attr_path, transform, mode, c_dim)
    
    data_loader = data.DataLoader(dataset=dataset,
                                  batch_size=batch_size,
                                  shuffle=(mode=='train'),
                                  num_workers=num_workers,
                                  drop_last=True)

    return data_loader