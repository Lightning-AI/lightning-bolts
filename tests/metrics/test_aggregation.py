"""Test Object Detection Metric Functions."""

import pytest
import torch

from pl_bolts.metrics.aggregation import mean, accuracy, precision_at_k

@pytest.mark.parametrize(
    "preds, expected_mean",
    [(torch.tensor([[100., 100., 200., 200.]]), 150.0)],
)
def test_mean(preds, expected_mean):
    x = {"test":preds}
    torch.testing.assert_allclose(mean([x], "test"), expected_mean)

@pytest.mark.parametrize(
    "preds, target, expected_accuracy",
    [
        (torch.tensor([[100, 100, 200, 200]]), torch.tensor([[2]]), torch.tensor(1.0)),
        (torch.tensor([[100, 100, 200, 200]]), torch.tensor([[0]]), torch.tensor(0.0))
    ],
)
def test_accuracy(preds, target, expected_accuracy):
    torch.testing.assert_allclose(accuracy(preds, target), expected_accuracy)