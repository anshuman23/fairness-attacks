import os
from abc import abstractmethod
from typing import Optional, List
from urllib.request import urlretrieve

import numpy as np
import pytorch_lightning as pl
import torch
from torch.utils.data import DataLoader

from dataset import Dataset


class Datamodule(pl.LightningDataModule):
    def __init__(self, file_name: str, sens_idx: int, adv_val: float, data_dir: str, batch_size: int):
        super().__init__()
        self.sens_idx = sens_idx
        self.adv_val = adv_val

        self.file_name = file_name
        self.data_dir = data_dir
        self.batch_size = batch_size

        self.path_to_file = os.path.join(self.data_dir, self.file_name)

        self.prepare_data()
        self.setup()

    def prepare_data(self) -> None:
        if not os.path.exists(self.data_dir):
            os.mkdir(self.data_dir)

        urlretrieve(
            url=f'https://raw.githubusercontent.com/Ninarehm/attack/master/Fairness_attack/data/{self.file_name}',
            filename=self.path_to_file
        )

    def setup(self, stage: Optional[str] = None) -> None:
        npz = np.load(self.path_to_file, allow_pickle=True)

        x_train, x_test = torch.tensor(npz['X_train']), torch.tensor(npz['X_test'])
        y_train, y_test = torch.tensor(npz['Y_train']), torch.tensor(npz['Y_test'])

        if stage in (None, 'fit'):
            self.train_data = Dataset(
                X=x_train,
                Y=y_train,
                adv_mask=self.__get_advantaged_mask(x_train)
            )

        if stage in (None, 'test'):
            self.test_data = Dataset(
                X=x_test,
                Y=y_test,
                adv_mask=self.__get_advantaged_mask(x_test)
            )

    def __get_advantaged_mask(self, features: torch.Tensor) -> torch.BoolTensor:
        sensitive_idx = self.sens_idx
        advantaged_value = self.adv_val

        return features[:, sensitive_idx] == advantaged_value

    def train_dataloader(self) -> DataLoader:
        return DataLoader(self.train_data, self.batch_size)

    def test_dataloader(self) -> DataLoader:
        return DataLoader(self.test_data, self.batch_size)

    def get_train_dataset(self) -> Dataset:
        return self.train_data
    
    def get_test_dataset(self) -> Dataset:
        return self.test_data
