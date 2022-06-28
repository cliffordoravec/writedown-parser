class SourceLine():
    """Contains information about a line of input."""

    def __init__(self, source, lineno, content):
        self.source = source
        """The file path of the source, or 'string' if string input."""
        self.lineno = lineno
        """The line number of this line."""
        self.content = content
        """The content of the line."""