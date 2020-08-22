from copy import deepcopy
import torch
import torch.nn.functional as F
import pytorch_lightning as pl
from typing import Any

from pl_bolts.datamodules import CIFAR10DataModule, STL10DataModule, ImagenetDataModule
from pl_bolts.models.self_supervised.simclr.simclr_transforms import SimCLREvalDataTransform, SimCLRTrainDataTransform
from pl_bolts.optimizers.layer_adaptive_scaling import LARS
from pl_bolts.optimizers.lr_scheduler import LinearWarmupCosineAnnealingLR
from pl_bolts.models.self_supervised.byol.models import SiameseArm
from pl_bolts.callbacks.self_supervised import BYOLMAWeightUpdate, SSLOnlineEvaluator


class BYOL(pl.LightningModule):
    def __init__(self,
                 datamodule: pl.LightningDataModule = None,
                 data_dir: str = './',
                 learning_rate: float = 0.2,
                 weight_decay: float = 15e-6,
                 input_height: int = 32,
                 batch_size: int = 32,
                 num_workers: int = 4,
                 warmup_epochs: int = 10,
                 max_epochs: int = 1000,
                 **kwargs):
        """
        PyTorch Lightning implementation of `Bring Your Own Latent (BYOL)
        <https://arxiv.org/pdf/2006.07733.pdf.>`_

        Paper authors: Jean-Bastien Grill ,Florian Strub, Florent Altché, Corentin Tallec, Pierre H. Richemond, \
        Elena Buchatskaya, Carl Doersch, Bernardo Avila Pires, Zhaohan Daniel Guo, Mohammad Gheshlaghi Azar, \
        Bilal Piot, Koray Kavukcuoglu, Rémi Munos, Michal Valko.

        Model implemented by:
            - `Annika Brundyn <https://github.com/annikabrundyn>`_

        .. warning:: Work in progress. This implementation is still being verified.

        TODOs:
            - verify on CIFAR-10
            - verify on STL-10
            - pre-train on imagenet

        Example:

            >>> from pl_bolts.models.self_supervised import BYOL
            ...
            >>> model = BYOL()

        Train::

            trainer = Trainer()
            trainer.fit(model)

        CLI command::

            # cifar10
            python byol_module.py --gpus 1

            # imagenet
            python byol_module.py
                --gpus 8
                --dataset imagenet2012
                --data_dir /path/to/imagenet/
                --meta_dir /path/to/folder/with/meta.bin/
                --batch_size 32

        Args:
            datamodule: The datamodule
            data_dir: directory to store data
            learning_rate: the learning rate
            weight_decay: optimizer weight decay
            input_height: image input height
            batch_size: the batch size
            num_workers: number of workers
            warmup_epochs: num of epochs for scheduler warm up
            max_epochs: max epochs for scheduler
        """
        super().__init__()
        self.save_hyperparameters()

        # init default datamodule
        if datamodule is None:
            datamodule = CIFAR10DataModule(data_dir, num_workers=num_workers, batch_size=batch_size)
            datamodule.train_transforms = SimCLRTrainDataTransform(input_height)
            datamodule.val_transforms = SimCLREvalDataTransform(input_height)

        self.datamodule = datamodule

        self.online_network = SiameseArm()
        self.target_network = deepcopy(self.online_network)

        self.weight_callback = BYOLMAWeightUpdate()

        # for finetuning callback
        self.z_dim = 2048
        self.num_classes = self.datamodule.num_classes

    def on_train_batch_end(self, batch: Any, batch_idx: int, dataloader_idx: int) -> None:
        # Add callback for user automatically since it's key to BYOL weight update
        self.weight_callback.on_batch_end(self.trainer, self)

    def forward(self, x):
        y, _, _ = self.online_network(x)
        return y

    def shared_step(self, batch, batch_idx):
        (img_1, img_2), y = batch

        # Image 1 to image 2 loss
        y1, z1, h1 = self.online_network(img_1)
        with torch.no_grad():
            y2, z2, h2 = self.target_network(img_2)
        # L2 normalize
        h1_norm = F.normalize(h1, p=2, dim=1)
        z2_norm = F.normalize(z2, p=2, dim=1)
        loss_a = F.mse_loss(h1_norm, z2_norm)

        # Image 2 to image 1 loss
        y1, z1, h1 = self.online_network(img_2)
        with torch.no_grad():
            y2, z2, h2 = self.target_network(img_1)
        # L2 normalize
        h1_norm = F.normalize(h1, p=2, dim=1)
        z2_norm = F.normalize(z2, p=2, dim=1)
        loss_b = F.mse_loss(h1_norm, z2_norm)

        # Final loss
        total_loss = loss_a + loss_b

        return loss_a, loss_b, total_loss

    def training_step(self, batch, batch_idx):
        loss_a, loss_b, total_loss = self.shared_step(batch, batch_idx)

        # log results
        result = pl.TrainResult(minimize=total_loss)
        result.log_dict({'1_2_loss': loss_a, '2_1_loss': loss_b, 'train_loss': total_loss})

        return result

    def validation_step(self, batch, batch_idx):
        loss_a, loss_b, total_loss = self.shared_step(batch, batch_idx)

        # log results
        result = pl.EvalResult(early_stop_on=total_loss, checkpoint_on=total_loss)
        result.log_dict({'1_2_loss': loss_a, '2_1_loss': loss_b, 'train_loss': total_loss})

        return result

    def configure_optimizers(self):
        optimizer = LARS(self.parameters(), lr=self.hparams.learning_rate, weight_decay=self.hparams.weight_decay)
        scheduler = LinearWarmupCosineAnnealingLR(
            optimizer,
            warmup_epochs=self.hparams.warmup_epochs,
            max_epochs=self.hparams.max_epochs
        )
        return [optimizer], [scheduler]

    @staticmethod
    def add_model_specific_args(parent_parser):
        parser = ArgumentParser(parents=[parent_parser], add_help=False)
        parser.add_argument('--online_ft', action='store_true', help='run online finetuner')
        parser.add_argument('--dataset', type=str, default='cifar10', help='cifar10, imagenet2012, stl10')

        (args, _) = parser.parse_known_args()

        # Data
        parser.add_argument('--data_dir', type=str, default='.')
        parser.add_argument('--num_workers', default=4, type=int)

        # optim
        parser.add_argument('--batch_size', type=int, default=256)
        parser.add_argument('--learning_rate', type=float, default=1e-3)
        parser.add_argument('--weight_decay', type=float, default=15e-6)
        parser.add_argument('--warmup_epochs', type=float, default=10)

        # Model
        parser.add_argument('--meta_dir', default='.', type=str, help='path to meta.bin for imagenet')

        return parser


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()

    # trainer args
    parser = pl.Trainer.add_argparse_args(parser)

    # model args
    parser = BYOL.add_model_specific_args(parser)
    args = parser.parse_args()

    # pick data
    datamodule = None
    if args.dataset == 'stl10':
        datamodule = STL10DataModule.from_argparse_args(args)
        datamodule.train_dataloader = datamodule.train_dataloader_mixed
        datamodule.val_dataloader = datamodule.val_dataloader_mixed

        (c, h, w) = datamodule.size()
        datamodule.train_transforms = SimCLRTrainDataTransform(h)
        datamodule.val_transforms = SimCLREvalDataTransform(h)

    elif args.dataset == 'imagenet2012':
        datamodule = ImagenetDataModule.from_argparse_args(args, image_size=196)
        (c, h, w) = datamodule.size()
        datamodule.train_transforms = SimCLRTrainDataTransform(h)
        datamodule.val_transforms = SimCLREvalDataTransform(h)

    model = BYOL(**args.__dict__, datamodule=datamodule)

    trainer = pl.Trainer.from_argparse_args(args, max_steps=10000, callbacks=[SSLOnlineEvaluator()])
    trainer.fit(model)
