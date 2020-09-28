import pytorch_lightning as pl
from pytorch_lightning import seed_everything

from pl_bolts.models import LitMNIST


def test_mnist(tmpdir):
    seed_everything()

    model = LitMNIST(data_dir=tmpdir, num_workers=0)
    trainer = pl.Trainer(limit_train_batches=0.01, limit_val_batches=0.01, max_epochs=1,
                         limit_test_batches=0.01, default_root_dir=tmpdir)
    trainer.fit(model)
    trainer.test(model)
    loss = trainer.callback_metrics['loss']

    assert loss <= 2.5, 'mnist failed'
