import pytorch_lightning as pl

from pl_bolts.datamodules.sklearn_dataloaders import SklearnDataLoaders
from tests import reset_seed
from sklearn.utils import shuffle as sk_shuffle
import numpy as np


def test_dataloader(tmpdir):
    reset_seed()

    X = np.random.rand(5, 2)
    y = np.random.rand(5)
    x_val = np.random.rand(2, 2)
    y_val = np.random.rand(2)
    x_test = np.random.rand(1, 2)
    y_test = np.random.rand(1)

    shuffled_X, shuffled_y = sk_shuffle(X, y, random_state=1234)

    # -----------------------------
    # train
    # -----------------------------
    loaders = SklearnDataLoaders(X=X, y=y, val_split=0.2, test_split=0.2, random_state=1234)
    train_loader = loaders.train_dataloader()
    val_loader = loaders.val_dataloader()
    test_loader = loaders.test_dataloader()
    assert np.all(train_loader.dataset.X == shuffled_X[2:])
    assert np.all(val_loader.dataset.X == shuffled_X[0])
    assert np.all(test_loader.dataset.X == shuffled_X[1])
    assert np.all(train_loader.dataset.Y == shuffled_y[2:])

    # -----------------------------
    # train + val
    # -----------------------------
    loaders = SklearnDataLoaders(X=X, y=y, x_val=x_val, y_val=y_val, test_split=0.2, random_state=1234)
    train_loader = loaders.train_dataloader()
    val_loader = loaders.val_dataloader()
    test_loader = loaders.test_dataloader()
    assert np.all(train_loader.dataset.X == shuffled_X[1:])
    assert np.all(val_loader.dataset.X == x_val)
    assert np.all(test_loader.dataset.X == shuffled_X[0])

    # -----------------------------
    # train + test
    # -----------------------------
    loaders = SklearnDataLoaders(X=X, y=y, x_test=x_test, y_test=y_test, val_split=0.2, random_state=1234)
    train_loader = loaders.train_dataloader()
    val_loader = loaders.val_dataloader()
    test_loader = loaders.test_dataloader()
    assert np.all(train_loader.dataset.X == shuffled_X[1:])
    assert np.all(val_loader.dataset.X == shuffled_X[0])
    assert np.all(test_loader.dataset.X == x_test)

    # -----------------------------
    # train + val + test
    # -----------------------------
    loaders = SklearnDataLoaders(X, y, x_val, y_val, x_test, y_test, random_state=1234)
    train_loader = loaders.train_dataloader()
    val_loader = loaders.val_dataloader()
    test_loader = loaders.test_dataloader()
    assert np.all(train_loader.dataset.X == shuffled_X)
    assert np.all(val_loader.dataset.X == x_val)
    assert np.all(test_loader.dataset.X == x_test)



test_dataloader('')