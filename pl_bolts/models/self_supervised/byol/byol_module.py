from argparse import ArgumentParser
from copy import deepcopy
from typing import Any, Tuple, Union

import torch
from pytorch_lightning import LightningModule, Trainer, seed_everything
from torch import Tensor
from torch.nn import functional as F
from torch.optim import Adam

from pl_bolts.callbacks.byol_updates import BYOLMAWeightUpdate
from pl_bolts.models.self_supervised.byol.models import SiameseArm
from pl_bolts.optimizers.lr_scheduler import LinearWarmupCosineAnnealingLR


class BYOL(LightningModule):
    """PyTorch Lightning implementation of Bootstrap Your Own Latent (BYOL_)_

    Paper authors: Jean-Bastien Grill, Florian Strub, Florent Altché, Corentin Tallec, Pierre H. Richemond, \
    Elena Buchatskaya, Carl Doersch, Bernardo Avila Pires, Zhaohan Daniel Guo, Mohammad Gheshlaghi Azar, \
    Bilal Piot, Koray Kavukcuoglu, Rémi Munos, Michal Valko.

    Args:
        num_classes (int): number of classes
        learning_rate (float, optional): optimizer learning rate. Defaults to 0.2.
        weight_decay (float, optional): optimizer weight decay. Defaults to 1.5e-6.
        input_height (int, optional): data input height. Defaults to 32.
        batch_size (int, optional): number of samples per batch. Defaults to 32.
        num_workers (int, optional): number of subprocesses used in loading data. Defaults to 0.
        warmup_epochs (int, optional): number of epochs for scheduler warmup. Defaults to 10.
        max_epochs (int, optional): maximum number of epochs for scheduler. Defaults to 1000.
        base_encoder (Union[str, torch.nn.Module], optional): base encoder architecture. Defaults to "resnet50".
        encoder_out_dim (int, optional): base encoder output dimension. Defaults to 2048.
        projector_hidden_size (int, optional): projector MLP hidden dimension. Defaults to 4096.
        projector_out_dim (int, optional): projector MLP output dimension. Defaults to 256.

    Example::

        model = BYOL(num_classes=10)

        dm = CIFAR10DataModule(num_workers=0)
        dm.train_transforms = SimCLRTrainDataTransform(32)
        dm.val_transforms = SimCLREvalDataTransform(32)

        trainer = pl.Trainer()
        trainer.fit(model, datamodule=dm)

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

    .. _BYOL: https://arxiv.org/pdf/2006.07733.pdf
    """

    def __init__(
        self,
        num_classes: int,
        learning_rate: float = 0.2,
        weight_decay: float = 1.5e-6,
        input_height: int = 32,
        batch_size: int = 32,
        num_workers: int = 0,
        warmup_epochs: int = 10,
        max_epochs: int = 1000,
        base_encoder: Union[str, torch.nn.Module] = "resnet50",
        encoder_out_dim: int = 2048,
        projector_hidden_size: int = 4096,
        projector_out_dim: int = 256,
        **kwargs: Any,
    ):
        super().__init__()
        self.save_hyperparameters(ignore="base_encoder")

        self.online_network = SiameseArm(base_encoder, encoder_out_dim, projector_hidden_size, projector_out_dim)
        self.target_network = deepcopy(self.online_network)
        self.weight_callback = BYOLMAWeightUpdate()

    def on_train_batch_end(self, outputs: Any, batch: Any, batch_idx: int) -> None:
        """Add callback to perform BYOL exponential moving average weight update on target network."""
        self.weight_callback.on_train_batch_end(self.trainer, self, outputs, batch, batch_idx)

    def forward(self, x: Tensor) -> Tensor:
        y, _, _ = self.online_network(x)
        return y

    def calculate_loss(self, v_online: Tensor, v_target: Tensor) -> Tensor:
        """Calculates similarity loss between the online network prediction of target network projection.

        Args:
            v_online (Tensor): Online network view
            v_target (Tensor): Target network view
        """
        _, _, h1 = self.online_network(v_online)
        with torch.no_grad():
            _, z2, _ = self.target_network(v_target)
        loss = -2 * F.cosine_similarity(h1, z2).mean()
        return loss

    def shared_step(self, batch: Any, batch_idx: int) -> Tuple[Tensor, Tensor, Tensor]:
        imgs, _ = batch
        img1, img2 = imgs[:2]

        # Calculate similarity loss in each direction
        loss_a = self.calculate_loss(img1, img2)
        loss_b = self.calculate_loss(img2, img1)

        # Calculate total loss
        total_loss = loss_a + loss_b

        return loss_a, loss_b, total_loss

    def training_step(self, batch: Any, batch_idx: int) -> Tensor:
        loss_a, loss_b, total_loss = self.shared_step(batch, batch_idx)
        self.log_dict({"1_2_loss": loss_a, "2_1_loss": loss_b, "train_loss": total_loss})

        return total_loss

    def validation_step(self, batch: Any, batch_idx: int) -> Tensor:
        loss_a, loss_b, total_loss = self.shared_step(batch, batch_idx)
        self.log_dict({"1_2_loss": loss_a, "2_1_loss": loss_b, "val_loss": total_loss})

        return total_loss

    def configure_optimizers(self):
        optimizer = Adam(self.parameters(), lr=self.hparams.learning_rate, weight_decay=self.hparams.weight_decay)
        scheduler = LinearWarmupCosineAnnealingLR(
            optimizer, warmup_epochs=self.hparams.warmup_epochs, max_epochs=self.hparams.max_epochs
        )
        return [optimizer], [scheduler]

    @staticmethod
    def add_model_specific_args(parent_parser) -> ArgumentParser:
        parser = ArgumentParser(parents=[parent_parser], add_help=False)
        parser.add_argument("--online_ft", action="store_true", help="run online finetuner")
        parser.add_argument("--dataset", type=str, default="cifar10", choices=["cifar10", "imagenet2012", "stl10"])

        (args, _) = parser.parse_known_args()

        # Data params
        parser.add_argument("--data_dir", type=str, default=".")
        parser.add_argument("--num_workers", default=8, type=int)

        # Training params
        parser.add_argument("--batch_size", type=int, default=256)
        parser.add_argument("--learning_rate", type=float, default=1e-3)
        parser.add_argument("--weight_decay", type=float, default=1.5e-6)
        parser.add_argument("--warmup_epochs", type=float, default=10)

        # Model params
        parser.add_argument("--meta_dir", default=".", type=str, help="path to meta.bin for imagenet")

        return parser


def cli_main():
    from pl_bolts.callbacks.ssl_online import SSLOnlineEvaluator
    from pl_bolts.datamodules import CIFAR10DataModule, ImagenetDataModule, STL10DataModule
    from pl_bolts.models.self_supervised.simclr import SimCLREvalDataTransform, SimCLRTrainDataTransform

    seed_everything(1234)

    parser = ArgumentParser()

    parser = Trainer.add_argparse_args(parser)
    parser = BYOL.add_model_specific_args(parser)

    args = parser.parse_args()

    # Initialize datamodule
    if args.dataset == "cifar10":
        dm = CIFAR10DataModule.from_argparse_args(args)
        dm.train_transforms = SimCLRTrainDataTransform(32)
        dm.val_transforms = SimCLREvalDataTransform(32)
        args.num_classes = dm.num_classes
    elif args.dataset == "stl10":
        dm = STL10DataModule.from_argparse_args(args)
        dm.train_dataloader = dm.train_dataloader_mixed
        dm.val_dataloader = dm.val_dataloader_mixed

        (c, h, w) = dm.dims
        dm.train_transforms = SimCLRTrainDataTransform(h)
        dm.val_transforms = SimCLREvalDataTransform(h)
        args.num_classes = dm.num_classes
    elif args.dataset == "imagenet2012":
        dm = ImagenetDataModule.from_argparse_args(args, image_size=196)
        (c, h, w) = dm.dims
        dm.train_transforms = SimCLRTrainDataTransform(h)
        dm.val_transforms = SimCLREvalDataTransform(h)
        args.num_classes = dm.num_classes
    else:
        raise ValueError(
            f"{args.dataset} is not a valid dataset. Dataset must be 'cifar10', 'stl10', or 'imagenet2012'."
        )

    model = BYOL(**args.__dict__)

    # finetune in real-time
    online_eval = SSLOnlineEvaluator(dataset=args.dataset, z_dim=2048, num_classes=dm.num_classes)

    trainer = Trainer.from_argparse_args(args, max_steps=300000, callbacks=[online_eval])

    trainer.fit(model, datamodule=dm)


if __name__ == "__main__":
    cli_main()
