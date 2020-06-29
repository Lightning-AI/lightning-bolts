"""
Double DQN
"""

from typing import Tuple

import torch
import torch.nn as nn

from pl_bolts.models.rl.dqn_model import DQN


class DoubleDQN(DQN):
    """
    Double Deep Q-network (DDQN)
    PyTorch Lightning implementation of `Double DQN <https://arxiv.org/pdf/1509.06461.pdf>`_

    Paper authors: Hado van Hasselt, Arthur Guez, David Silver

    Model implemented by:

        - `Donal Byrne <https://github.com/djbyrne>`

    Example:

        >>> from pl_bolts.models.rl.double_dqn_model import DoubleDQN
        ...
        >>> model = DoubleDQN("PongNoFrameskip-v4")

    Train::

        trainer = Trainer()
        trainer.fit(model)

    Args:
        env: gym environment tag
        gpus: number of gpus being used
        eps_start: starting value of epsilon for the epsilon-greedy exploration
        eps_end: final value of epsilon for the epsilon-greedy exploration
        eps_last_frame: the final frame in for the decrease of epsilon. At this frame espilon = eps_end
        sync_rate: the number of iterations between syncing up the target network with the train network
        gamma: discount factor
        lr: learning rate
        batch_size: size of minibatch pulled from the DataLoader
        replay_size: total capacity of the replay buffer
        warm_start_size: how many random steps through the environment to be carried out at the start of
            training to fill the buffer with a starting point
        sample_len: the number of samples to pull from the dataset iterator and feed to the DataLoader

    .. note::
        This example is based on:
         https://github.com/PacktPublishing/Deep-Reinforcement-Learning-Hands-On-Second-Edition\
         /blob/master/Chapter08/03_dqn_double.py

    .. note:: Currently only supports CPU and single GPU training with `distributed_backend=dp`

    """

    def loss(self, batch: Tuple[torch.Tensor, torch.Tensor]) -> torch.Tensor:
        """
        Calculates the mse loss using a mini batch from the replay buffer. This uses an improvement to the original
        DQN loss by using the double dqn. This is shown by using the actions of the train network to pick the
        value from the target network. This code is heavily commented in order to explain the process clearly

        Args:
            batch: current mini batch of replay data

        Returns:
            loss
        """
        states, actions, rewards, dones, next_states = batch  # batch of experiences, batch_size = 16

        actions_v = actions.unsqueeze(-1)  # adds a dimension, 16 -> [16, 1]
        output = self.net(states)  # shape [16, 2], [batch, action space]

        # gather the value of the outputs according to the actions index from the batch
        state_action_values = output.gather(1, actions_v).squeeze(-1)

        # dont want to mess with gradients when using the target network
        with torch.no_grad():
            next_outputs = self.net(next_states)  # [16, 2], [batch, action_space]

            next_state_acts = next_outputs.max(1)[1].unsqueeze(
                -1
            )  # take action at the index with the highest value
            next_tgt_out = self.target_net(next_states)

            # Take the value of the action chosen by the train network
            next_state_values = next_tgt_out.gather(1, next_state_acts).squeeze(-1)
            next_state_values[dones] = 0.0  # any steps flagged as done get a 0 value
            next_state_values = (
                next_state_values.detach()
            )  # remove values from the graph, no grads needed

        # calc expected discounted return of next_state_values
        expected_state_action_values = next_state_values * self.gamma + rewards

        # Standard MSE loss between the state action values of the current state and the
        # expected state action values of the next state
        return nn.MSELoss()(state_action_values, expected_state_action_values)
