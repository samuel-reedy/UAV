# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/api/04_utils.general.ipynb.

# %% auto 0
__all__ = ['LeakyQueue']

# %% ../../nbs/api/04_utils.general.ipynb 3
from fastcore.utils import *
from fastcore.utils import *

import queue
import typing as typ

# %% ../../nbs/api/04_utils.general.ipynb 4
class LeakyQueue(queue.Queue):
    """Queue that contains only the last actual items and drops the oldest one."""

    def __init__(
        self,
        maxsize: int = 100,
        on_drop: typ.Optional[typ.Callable[["LeakyQueue", "object"], None]] = None,
    ):
        super().__init__(maxsize=maxsize)
        self._dropped = 0
        self._on_drop = on_drop or (lambda queue, item: None)

    def put(self, item, block=True, timeout=None):
        if self.full():
            dropped_item = self.get_nowait()
            self._dropped += 1
            self._on_drop(self, dropped_item)
        super().put(item, block=block, timeout=timeout)

    @property
    def dropped(self):
        return self._dropped