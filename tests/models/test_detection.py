import torch
from pytorch_lightning import Trainer
from torch.utils.data import DataLoader

from pl_bolts.datasets import DummyDetectionDataset
from pl_bolts.models.detection import FasterRCNN, RetinaNet


def _collate_fn(batch):
    return tuple(zip(*batch))


@torch.no_grad()
def test_fasterrcnn():
    model = FasterRCNN(pretrained=False, pretrained_backbone=False)

    image = torch.rand(1, 3, 224, 224)
    model(image)


def test_fasterrcnn_train(tmpdir):
    model = FasterRCNN(pretrained=False, pretrained_backbone=False)

    train_dl = DataLoader(DummyDetectionDataset(), collate_fn=_collate_fn)
    valid_dl = DataLoader(DummyDetectionDataset(), collate_fn=_collate_fn)

    trainer = Trainer(fast_dev_run=True, default_root_dir=tmpdir)
    trainer.fit(model, train_dataloader=train_dl, val_dataloaders=valid_dl)


def test_fasterrcnn_bbone_train(tmpdir):
    model = FasterRCNN(backbone="resnet18", fpn=True, pretrained_backbone=False)
    train_dl = DataLoader(DummyDetectionDataset(), collate_fn=_collate_fn)
    valid_dl = DataLoader(DummyDetectionDataset(), collate_fn=_collate_fn)

    trainer = Trainer(fast_dev_run=True, logger=False, checkpoint_callback=False, default_root_dir=tmpdir)
    trainer.fit(model, train_dl, valid_dl)


@torch.no_grad()
def test_retinanet():
    model = RetinaNet(pretrained=False)

    image = torch.rand(1, 3, 400, 400)
    model(image)


def test_retinanet_train(tmpdir):
    model = RetinaNet(pretrained=False)

    train_dl = DataLoader(DummyDetectionDataset(), collate_fn=_collate_fn)
    valid_dl = DataLoader(DummyDetectionDataset(), collate_fn=_collate_fn)

    trainer = Trainer(fast_dev_run=True, logger=False, checkpoint_callback=False, default_root_dir=tmpdir)
    trainer.fit(model, train_dataloader=train_dl, val_dataloaders=valid_dl)


def test_retinanet_backbone_train(tmpdir):
    model = RetinaNet(backbone="resnet18", fpn=True, pretrained_backbone=False)
    train_dl = DataLoader(DummyDetectionDataset(), collate_fn=_collate_fn)
    valid_dl = DataLoader(DummyDetectionDataset(), collate_fn=_collate_fn)

    trainer = Trainer(fast_dev_run=True, logger=False, checkpoint_callback=False, default_root_dir=tmpdir)
    model = FasterRCNN(backbone="resnet18", fpn=True, pretrained_backbone=False, pretrained=False)
    train_dl = DataLoader(DummyDetectionDataset(), collate_fn=_collate_fn)
    valid_dl = DataLoader(DummyDetectionDataset(), collate_fn=_collate_fn)

    trainer = Trainer(fast_dev_run=True, default_root_dir=tmpdir)
    trainer.fit(model, train_dl, valid_dl)
