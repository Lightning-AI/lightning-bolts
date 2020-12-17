import os
from abc import abstractmethod
from typing import List, Optional, Tuple, Union

import torch
from pytorch_lightning import LightningDataModule
from torch.utils.data import DataLoader, Dataset, random_split


class VisionDataModule(LightningDataModule):

    EXTRA_ARGS = {}
    #: Dataset class to use
    DATASET_CLASS = ...
    name: str = ""
    #: A tuple describing the shape of the data
    DIMS: tuple = ...

    def __init__(
        self,
        data_dir: Optional[str] = None,
        val_split: Union[int, float] = 0.2,
        num_workers: int = 16,
        normalize: bool = False,
        seed: int = 42,
        batch_size: int = 32,
        *args,
        **kwargs,
    ):
        """
        Args:
            data_dir: Where to save/load the data
            val_split: Percent (float) or number (int) of samples to use for the validation split
            num_workers: How many workers to use for loading data
            normalize: If true applies image normalize
            seed: Seed to fix the validation split
            batch_size: How many samples per batch to load
        """

        super().__init__(*args, **kwargs)

        self.data_dir = data_dir if data_dir is not None else os.getcwd()
        self.val_split = val_split
        self.num_workers = num_workers
        self.normalize = normalize
        self.seed = seed
        self.batch_size = batch_size

    def prepare_data(self):
        """
        Saves files to data_dir
        """
        self.DATASET_CLASS(self.data_dir, train=True, download=True)
        self.DATASET_CLASS(self.data_dir, train=False, download=True)

    def setup(self, stage: Optional[str] = None):
        """
        Creates train, val, and test dataset
        """
        if stage == "fit" or stage is None:
            train_transforms = self.default_transforms() if self.train_transforms is None else self.train_transforms
            val_transforms = self.default_transforms() if self.val_transforms is None else self.val_transforms

            dataset_train = self.DATASET_CLASS(self.data_dir, train=True, transform=train_transforms, **self.EXTRA_ARGS)
            dataset_val = self.DATASET_CLASS(self.data_dir, train=True, transform=val_transforms, **self.EXTRA_ARGS)

            # Split
            self.dataset_train = self._split_dataset(dataset_train)
            self.dataset_val = self._split_dataset(dataset_val, train=False)

        if stage == "test" or stage is None:
            test_transforms = self.default_transforms() if self.test_transforms is None else self.test_transforms
            self.dataset_test = self.DATASET_CLASS(
                self.data_dir, train=False, transform=test_transforms, **self.EXTRA_ARGS
            )

    def _split_dataset(self, dataset: Dataset, train: bool = True) -> Dataset:
        """
        Splits the dataset into train and validation set
        """
        len_dataset = len(dataset)
        splits = self._get_splits(len_dataset)
        dataset_train, dataset_val = random_split(
            dataset, splits, generator=torch.Generator().manual_seed(self.seed)
        )

        if train:
            return dataset_train
        return dataset_val

    def _get_splits(self, len_dataset: int) -> List[int]:
        """
        Computes split lengths for train and validation set
        """
        if isinstance(self.val_split, int):
            train_len = len_dataset - self.val_split
            splits = [train_len, self.val_split]
        elif isinstance(self.val_split, float):
            val_len = int(self.val_split * len_dataset)
            train_len = len_dataset - val_len
            splits = [train_len, val_len]
        else:
            raise ValueError(f'Unsupported type {type(self.val_split)}')

        return splits

    @abstractmethod
    def default_transforms(self):
        """ Default transform for the dataset """

    def train_dataloader(self) -> DataLoader:
        """ The train dataloader """
        return self._data_loader(self.dataset_train, shuffle=True)

    def val_dataloader(self) -> DataLoader:
        """ The val dataloader """
        return self._data_loader(self.dataset_val)

    def test_dataloader(self) -> DataLoader:
        """ The test dataloader """
        return self._data_loader(self.dataset_test)

    def _data_loader(self, dataset: Dataset, shuffle: bool = False) -> DataLoader:
        return DataLoader(
            dataset,
            batch_size=self.batch_size,
            shuffle=shuffle,
            num_workers=self.num_workers,
            drop_last=True,
            pin_memory=True,
        )
