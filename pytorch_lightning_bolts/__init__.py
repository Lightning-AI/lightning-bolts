"""Root package info."""

import os
from pytorch_lightning_bolts.mnist_template import LitMNISTModel

__version__ = '0.1.0-dev5'
__author__ = 'PyTorchLightning et al.'
__author_email__ = 'name@pytorchlightning.ai'
__license__ = 'TBD'
__copyright__ = 'Copyright (c) 2020-2020, %s.' % __author__
__homepage__ = 'https://github.com/PyTorchLightning/pytorch-lightning-bolts'
__docs__ = "PyTorch Lightning Bolts is a community contribution for ML researchers."

PACKAGE_ROOT = os.path.dirname(__file__)
