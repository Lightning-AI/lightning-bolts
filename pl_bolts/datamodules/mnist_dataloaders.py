from torch.utils.data import DataLoader, random_split
from torchvision import transforms as transform_lib
from torchvision.datasets import MNIST
import os

from pl_bolts.datamodules.bolts_dataloaders_base import LightningDataModule


class MNISTDataModule(LightningDataModule):

    def __init__(self, data_dir: str = os.getcwd(), val_split: int = 5000, num_workers: int = 16):
        super().__init__()
        self.data_dir = data_dir
        self.val_split = val_split
        self.num_workers = num_workers

    @property
    def num_classes(self):
        return 10

    def prepare_data(self):
        MNIST(self.data_dir, train=True, download=True, transform=transform_lib.ToTensor())
        MNIST(self.data_dir, train=False, download=True, transform=transform_lib.ToTensor())

    def train_dataloader(self, batch_size, transforms=None, use_default_normalize=True):
        if transforms is None:
            transforms = self._default_transforms()

        dataset = MNIST(self.data_dir, train=True, download=False, transform=transforms)
        train_length = len(dataset)
        dataset_train, _ = random_split(dataset, [train_length - self.val_split, self.val_split])
        loader = DataLoader(
            dataset_train,
            batch_size=batch_size,
            shuffle=True,
            num_workers=self.num_workers,
            drop_last=True,
            pin_memory=True
        )
        return loader

    def val_dataloader(self, batch_size, transforms=None, use_default_normalize=True):
        if transforms is None:
            transforms = self._default_transforms()

        dataset = MNIST(self.data_dir, train=True, download=True, transform=transforms)
        train_length = len(dataset)
        _, dataset_val = random_split(dataset, [train_length - self.val_split, self.val_split])
        loader = DataLoader(
            dataset_val,
            batch_size=batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            drop_last=True,
            pin_memory=True
        )
        return loader

    def test_dataloader(self, batch_size, transforms=None, use_default_normalize=True):
        if transforms is None:
            transforms = self._default_transforms()

        dataset = MNIST(self.data_dir, train=False, download=False, transform=transforms)
        loader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            drop_last=True,
            pin_memory=True
        )
        return loader

    def _default_transforms(self):
        mnist_transforms = transform_lib.Compose([
            transform_lib.ToTensor()
        ])
        return mnist_transforms

    def size(self):
        return 1, 28, 28
