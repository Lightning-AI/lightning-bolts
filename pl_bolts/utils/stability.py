# Copyright The PyTorch Lightning team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import functools
import inspect
from typing import Callable, Optional, Type, Union
from warnings import filterwarnings

from pytorch_lightning.utilities import rank_zero_warn


class ReviewNeededWarning(Warning):
    pass


def _create_full_message(message: str) -> str:
    return (
        f"{message} The compatibility with other Lightning projects is not guaranteed and API may change at any time. "
        "The API and functionality may change without warning in future releases. "
        "More details: https://lightning-bolts.readthedocs.io/en/latest/stability.html"
    )


def _create_docstring_message(docstring: str, message: str) -> str:
    rst_warning = ".. warning:: " + _create_full_message(message)
    if docstring is None:
        return rst_warning
    return rst_warning + "\n\n    " + docstring


def _add_message_to_docstring(callable: Union[Callable, Type], message: str) -> Union[Callable, Type]:
    callable.__doc__ = _create_docstring_message(callable.__doc__, message)
    return callable


def _raise_review_warning(message: str, stacklevel: int = 6) -> None:
    rank_zero_warn(_create_full_message(message), stacklevel=stacklevel, category=ReviewNeededWarning)


def to_review():
    """The to_review decorator is used to indicate that a particular feature is not properly reviewed and tested yet.
    A callable or type that has been marked as to_review will give a ``ReviewNeededWarning`` when it is called or
    instantiated. This designation should be used following the description given in :ref:`stability`.
    Args:
        message: The message to include in the warning.
    Examples
    ________
    >>> from pytest import warns
    >>> from pl_bolts.utils.stability import to_review, ReviewNeededWarning
    >>> @to_review()
    ... class MyExperimentalFeature:
    ...     pass
    ...
    >>> with warns(ReviewNeededWarning, match="The feature MyExperimentalFeature is currently marked for review."):
    ...     MyExperimentalFeature()  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    ...
    <...>
    """

    def decorator(callable: Union[Callable, Type], message_name: Optional[str] = None):
        if message_name is None:
            message_name = callable.__qualname__

        message = f"The feature {message_name} is currently marked for review."
        filterwarnings("once", message, ReviewNeededWarning)
        if inspect.isclass(callable):
            if not hasattr(callable.__init__, "__wrapped__"):
                callable.__init__ = decorator(callable.__init__, message_name=message_name)
                return _add_message_to_docstring(callable, message)
            return callable

        @functools.wraps(callable)
        def wrapper(*args, **kwargs):
            _raise_review_warning(message)
            return callable(*args, **kwargs)

        return _add_message_to_docstring(wrapper, message)

    return decorator
