# PyTorchLightning Bolts

[![CircleCI](https://circleci.com/gh/PyTorchLightning/pytorch-lightning-bolts/tree/master.svg?style=svg)](https://circleci.com/gh/PyTorchLightning/pytorch-lightning-bolts/tree/master)
[![codecov](https://codecov.io/gh/PyTorchLightning/pytorch-lightning-bolts/branch/master/graph/badge.svg)](https://codecov.io/gh/PyTorchLightning/pytorch-lightning-bolts)
[![CodeFactor](https://www.codefactor.io/repository/github/pytorchlightning/pytorch-lightning-bolts/badge)](https://www.codefactor.io/repository/github/pytorchlightning/pytorch-lightning-bolts)
[![Documentation Status](https://readthedocs.org/projects/lightning-bolts/badge/?version=latest)](https://lightning-bolts.readthedocs.io/en/latest/?badge=latest)
[![Slack](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://join.slack.com/t/pytorch-lightning/shared_invite/enQtODU5ODIyNTUzODQwLTFkMDg5Mzc1MDBmNjEzMDgxOTVmYTdhYjA1MDdmODUyOTg2OGQ1ZWZkYTQzODhhNzdhZDA3YmNhMDhlMDY4YzQ)

## Install
```pip install pytorch-lightning-bolts```

## What is it?
Bolts is a collection of useful models and templates to bootstrap your DL research even faster.
It's designed to work  with PyTorch Lightning

## Example
```python

from pytorch_lightning_bolts.vaes import VAE
from pytorch_lightning_bolts.gans import CycleGAN
from pytorch_lightning import Trainer

vae = VAE()
gan = CycleGAN()

# train VAE
vae_trainer = Trainer()
vae_trainer.fit(vae)

# train GAN
gan_trainer = Trainer()
gan_trainer.fit(gan)
```

## How to add a model
This repository is meant for model contributions from the community.
To add a model, you can start with the MNIST template (or any other model in the repo).

Please organize the functions of your lightning module in this order.

```python
class MyModule(pl.LightningModule):
    
    # model
    def __init__(self):
    
    # computations
    def forward(self, x):
    
    # training loop
    def training_step(self, batch, batch_idx):
    
    # validation loop
    def validation_step(self, batch, batch_idx):
    def validation_end(self, outputs):
     
    # test loop
    def test_step(self, batch, batch_idx):
    def test_epoch_end(self, outputs):
    
    # optimizer
    def configure_optimizers(self):
    
    # data
    def prepare_data(self):
    def train_dataloader(self):
    def val_dataloader(self):
    def test_dataloader(self):
```
