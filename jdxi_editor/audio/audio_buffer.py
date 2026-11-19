"""
A preallocated stereo ring.

The capture callback is the only writer. The analysis worker is the only
reader. Neither side allocates, and the reader copies out so a later write
cannot change a buffer the worker is still using.
"""

import numpy as np


class SampleRing:
    """
    The most recent stereo frames, overwriting the oldest.

    ``capacity`` is the number of frames kept. Writes larger than that keep
    only the tail; capture blocks are far smaller, so the callback never
    takes that path.
    """

    def __init__(self, capacity: int):
        """
        :param capacity: int frames retained
        """
        if capacity < 2:
            raise ValueError("capacity must be at least 2")
        self.capacity = int(capacity)
        self.buffer = np.zeros((self.capacity, 2), dtype=np.float32)
        self._write = 0

    def written(self) -> int:
        """
        Frames accepted since the ring was created.

        :return: int
        """
        return self._write

    def write(self, frames: np.ndarray) -> None:
        """
        Copy ``frames`` in. Shape ``(n,)`` or ``(n, 1)`` is written to both
        channels. Shape ``(n, 2)`` is stereo.

        :param frames: np.ndarray samples
        :return: None
        """
        if frames.ndim == 1:
            count = int(frames.shape[0])
            channels = 1
        else:
            count = int(frames.shape[0])
            channels = int(frames.shape[1])
        if count <= 0:
            return
        if count > self.capacity:
            frames = frames[-self.capacity :]
            count = self.capacity
        start = self._write % self.capacity
        end = start + count
        if channels == 1:
            column = frames if frames.ndim == 1 else frames[:, 0]
            if end <= self.capacity:
                self.buffer[start:end, 0] = column
                self.buffer[start:end, 1] = column
            else:
                first = self.capacity - start
                self.buffer[start:, 0] = column[:first]
                self.buffer[start:, 1] = column[:first]
                self.buffer[: count - first, 0] = column[first:]
                self.buffer[: count - first, 1] = column[first:]
        else:
            stereo = frames[:, :2]
            if end <= self.capacity:
                self.buffer[start:end] = stereo
            else:
                first = self.capacity - start
                self.buffer[start:] = stereo[:first]
                self.buffer[: count - first] = stereo[first:]
        self._write += count

    def latest(self, count: int) -> np.ndarray:
        """
        A copy of the newest ``count`` frames, shape ``(n, 2)``.

        :param count: int frames wanted
        :return: np.ndarray
        """
        write = self._write
        count = min(int(count), write, self.capacity)
        out = np.empty((count, 2), dtype=np.float32)
        if count <= 0:
            return out
        end = write % self.capacity
        start = (write - count) % self.capacity
        if start < end:
            out[:] = self.buffer[start:end]
        elif end == 0:
            out[:] = self.buffer[start:]
        else:
            first = self.capacity - start
            out[:first] = self.buffer[start:]
            out[first:] = self.buffer[:end]
        return out
