import numpy as np
import torch
from PIL import Image

from pl_bolts.models.self_supervised.simclr.transforms import (
    SimCLREvalDataTransform,
    SimCLRFinetuneTransform,
    SimCLRTrainDataTransform,
)


def test_simclr_train_data_transform():
    # dummy image
    img = np.random.randint(low=0, high=255, size=(250, 250, 3), dtype=np.uint8)
    img = Image.fromarray(img)

    # size of the generated views
    input_height = 96
    transform = SimCLRTrainDataTransform(input_height=input_height)
    views = transform(img)

    # the transform must output a list or a tuple of images
    assert isinstance(views, (list, tuple))

    # the transform must output three images
    # (1st view, 2nd view, online evaluation view)
    assert len(views) == 3

    # all views are tensors
    assert all([torch.is_tensor(v) for v in views])

    # all views have expected sizes
    assert all([v.size(1) == v.size(2) == input_height for v in views])


def test_simclr_eval_data_transform():
    # dummy image
    img = np.random.randint(low=0, high=255, size=(250, 250, 3), dtype=np.uint8)
    img = Image.fromarray(img)

    # size of the generated views
    input_height = 96
    transform = SimCLREvalDataTransform(input_height=input_height)
    views = transform(img)

    # the transform must output a list or a tuple of images
    assert isinstance(views, (list, tuple))

    # the transform must output three images
    # (1st view, 2nd view, online evaluation view)
    assert len(views) == 3

    # all views are tensors
    assert all([torch.is_tensor(v) for v in views])

    # all views have expected sizes
    assert all([v.size(1) == v.size(2) == input_height for v in views])


def test_simclr_finetune_transform():
    # dummy image
    img = np.random.randint(low=0, high=255, size=(250, 250, 3), dtype=np.uint8)
    img = Image.fromarray(img)

    # size of the generated views
    input_height = 96
    transform = SimCLRFinetuneTransform(input_height=input_height)
    view = transform(img)

    # the view generator is a tensor
    assert torch.is_tensor(view)

    # view has expected size
    assert view.size(1) == view.size(2) == input_height
