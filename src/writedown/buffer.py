from typing import AnyStr

class IndexedGeneratorBuffer():
    """Wraps a generator to performed buffered reading (and rereading) of generator-yielded content as well as index-based retrieval of content."""

    def __init__(self, gen):
        self.gen = gen
        """The wrapped generator."""
        self.buffer = []
        """The internal buffer."""
        self.offset = 0
        """The offset between indices between the internal buffer representation and the exposed representation."""
        self.consumed = 0
        """The number of yields consumed from the generator."""

    def truncate(self, pos:int) -> None:
        """
        Truncates the contents of the internal buffer from the beginning of the buffer to the position specified.

        Used to eject fully consumed data that is no longer needed from memory.  Preserves an offset of the 
        truncated contents so that future requests to retrieve data by index do not need adjusting.
        """
        self.buffer[:(pos - self.offset)] = []
        self.offset = pos

    def read(self, length:int=1) -> None:
        """Reads the next value(s) from the generator, as specified by the length to read."""
        for i in range(0, length):
            self.buffer.append(next(self.gen))
            self.consumed += 1

    def valid_index(self, pos:int) -> bool:
        """Returns True if the index can be requested (even if reading is required) and False if not."""
        if pos < self.consumed: return True
        try:
            self.read(pos + 1 - self.consumed)
            return True
        except StopIteration:
            return False

    def get(self, pos:int) -> AnyStr:
        """Returns (even if reading is required) the data at the specified index (makes a generator accessible like a list)."""
        if pos >= self.consumed:
            self.read(pos + 1 - self.consumed)
        target = pos - self.offset
        if target < 0 or target >= len(self.buffer):
            raise IndexError()
        return self.buffer[target]