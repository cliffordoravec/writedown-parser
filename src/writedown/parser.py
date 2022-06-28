from datetime import datetime
import glob
import os
import re
from typing import Dict, Generator, Iterable, List
import warnings

from .ast import ActNode, ASTNode, AuthorNode, ChapterNode, CharacterNode, CommentNode, DocumentNode, LocationNode, PageBreakNode, PartNode, PlaceNode, SceneNode, SectionNode, SessionAttribute, StatusNode, TableOfContentsNode, TagNode, TargetNode, TextNode, TitleNode, TodoNode, UnmappedInstructionNode
from .buffer import IndexedGeneratorBuffer
from .sourceline import SourceLine
from .tokens import Tokens

class SequenceWarning(UserWarning):
    """Used to warn about issues in structural node sequences (e.g., out of sequence Chapter numbers)."""
    pass

class Parser():
    """A parser for Writedown content."""

    def __init__(self, sequences:Dict[str, int]=None):
        self.sequences = sequences if sequences != None else {}
        """A dict for tracking sequence numbers for structural nodes such as Chapters and Scenes."""

    def sequence_key(self, node_holder:ASTNode, structural_type:str) -> str:
        """
        Returns a dict key for tracking sequences for the given structural type in the context of the given node holder.

        The structural_type is a string because this method should be invoked prior to creation of the corresponding ASTNode instance.
        """
        return f'{node_holder.structural_path()} [{structural_type}]'

    def next_sequence(self, node_holder:ASTNode, structural_type:str) -> int:
        """
        Returns the next sequence number for the given structural type in the context of the given node holder.

        The structural_type is a string because this method should be invoked prior to creation of the corresponding ASTNode instance.
        """
        key = self.sequence_key(node_holder, structural_type)
        if not key in self.sequences:
            self.sequences[key] = 0
        self.sequences[key] += 1
        return self.sequences[key]

    def set_sequence(self, node_holder:ASTNode, structural_type:str, number:int) -> None:
        """
        Sets the current sequence number for the given structural type in the context of the given node holder.

        The structural_type is a string because this method should be invoked prior to creation of the corresponding ASTNode instance.
        """
        key = self.sequence_key(node_holder, structural_type)
        if key in self.sequences:
            existing = self.sequences[key]
            # TODO: Pass the source line and include that information in the warning message:
            if existing > number:
                warnings.warn(f'{structural_type} {number}: Sequence is less than previous sequence {structural_type} {existing}.', SequenceWarning)
            elif existing == number:
                warnings.warn(f'{structural_type} {number}: Sequence is the same as previous sequence {structural_type} {existing}.', SequenceWarning)
            elif existing < number - 1:
                warnings.warn(f'{structural_type} {number}: Sequence contains a gap from previous sequence {structural_type} {existing}.', SequenceWarning)
        self.sequences[key] = number

    def get_or_set_sequence(self, node_holder:ASTNode, structural_type:str, number:int) -> int:
        """
        Gets the next or sets the current sequence number for the given structrual type in the context of the given node holder
        based on the value of number.

        If number is None, the next sequence number is retrieved.  Otherwise, number is set as the current sequence number.
        """
        if number == None:
            return self.next_sequence(node_holder, structural_type)
        self.set_sequence(node_holder, structural_type, number)
        return number

    def strip_instruction(self, str:str) -> str:
        """
        Removes leading Writedown instructions from a string.

        For example, "@chapter One" would be returned as "One".
        """
        regex = '^\\' + Tokens.INSTRUCTION + '[^\s]+\s*'
        return re.sub(regex, '', str).strip()

    def is_instruction(self, text:str, token:Tokens) -> bool:
        """Returns True if the given text starts with the given Writedown instruction token."""
        return text.startswith(token.value)

    def get_instruction(self, str:str) -> str:
        """
        Returns the leading Writedown instruction token for the given string; returns None if one is not present.

        For example, "@chapter One" would return "@chapter".
        """
        regex = '^(\\' + Tokens.INSTRUCTION + '[^\s]+)'
        match = re.match(regex, str)
        if match:
            return match.group(0)
        return None

    def set_session_template(self, node_holder:ASTNode, session_template:SessionAttribute) -> None:
        """Sets the session template for the given node holder and all its ancestors."""
        me = node_holder
        while me != None:
            me.session_template = session_template
            me = me.parent

    def parse(self, node_holder:ASTNode, lines:IndexedGeneratorBuffer, pos:int=0, end:int=None) -> int:
        """
        Parses the supplied lines for Writedown markup, starting and ending at the provided index positions
        (inclusive and exclusive, respectively), in the context of the given node holder.  

        Returns the (unprocessed) index from which subsequent parsing should resume, if any.
        """
        while lines.valid_index(pos) and (end == None or end > pos):
            line = lines.get(pos)

            if self.is_instruction(line.content, Tokens.INSTRUCTION):
                instruction = self.get_instruction(line.content)

                match instruction:
                    case Tokens.EOF:
                        self.set_session_template(node_holder, None)
                        pos += 1

                    case Tokens.ACT:
                        pos = ActParser(self.sequences).parse(node_holder, lines, pos)

                    case Tokens.AUTHOR:
                        node_holder.append(AuthorNode(line, self.strip_instruction(line.content)))
                        pos += 1

                    case Tokens.CHAPTER:
                        pos = ChapterParser(self.sequences).parse(node_holder, lines, pos)

                    case Tokens.CHARACTER:
                        pos = CharacterParser(self.sequences).parse(node_holder, lines, pos)

                    case Tokens.COMMENT | Tokens.COMMENT_SHORTHAND:
                        node_holder.append(CommentNode(line, self.strip_instruction(line.content)))
                        pos += 1

                    case Tokens.COMMENT_BLOCK_START:
                        pos = CommentBlockParser(self.sequences).parse(node_holder, lines, pos)

                    case Tokens.END_SESSION:
                        self.set_session_template(node_holder, None)
                        pos += 1

                    case Tokens.INCLUDE:
                        path = self.strip_instruction(line.content)
                        if line.source != 'string':
                            path = os.path.join(os.path.dirname(line.source), path)
                        # Must create a new Parser instance here in case an @include is being processed
                        # by one of the subparsers (their parse() method will override this method,
                        # which is not what we would want):
                        node_holder.extend(Parser(self.sequences).parse_path(path))
                        pos += 1

                    case Tokens.LOCATION:
                        pos = LocationParser(self.sequences).parse(node_holder, lines, pos)

                    case Tokens.PAGEBREAK:
                        node_holder.append(PageBreakNode(line))
                        pos += 1

                    case Tokens.PART:
                        pos = PartParser(self.sequences).parse(node_holder, lines, pos)

                    case Tokens.PLACE:
                        pos = PlaceParser(self.sequences).parse(node_holder, lines, pos)

                    case Tokens.SCENE:
                        pos = SceneParser(self.sequences).parse(node_holder, lines, pos)

                    case Tokens.SECTION:
                        pos = SectionParser(self.sequences).parse(node_holder, lines, pos)

                    case Tokens.SESSION:
                        session_node = SessionParser(self.sequences).get_session_node(line)
                        self.set_session_template(node_holder, session_node)
                        pos += 1

                    case Tokens.STATUS:
                        node_holder.append(StatusNode(line, self.strip_instruction(line.content)))
                        pos += 1

                    case Tokens.TABLE_OF_CONTENTS | Tokens.TOC:
                        node_holder.append(TableOfContentsNode(line))
                        pos += 1

                    case Tokens.TAG:
                        tags = self.strip_instruction(line.content).split(' ')
                        node_holder.append(TagNode(line, tags))
                        pos += 1

                    case Tokens.TARGET:
                        wordcount = int(self.strip_instruction(line.content))
                        node_holder.append(TargetNode(line, wordcount))
                        pos += 1

                    case Tokens.TITLE:
                        node_holder.append(TitleNode(line, self.strip_instruction(line.content)))
                        pos += 1

                    case Tokens.TODO:
                        node_holder.append(TodoNode(line, self.strip_instruction(line.content)))
                        pos += 1

                    case _:
                        node_holder.append(UnmappedInstructionNode(line, instruction, self.strip_instruction(line.content)))
                        pos += 1
            else:
                node_holder.append(TextNode(line, line.content))
                pos += 1

        # Purge processed lines:
        lines.truncate(pos - 1)

        return pos

    def parse_str(self, str:str) -> List[ASTNode]:
        """Parses the provided string and returns a list of ASTNodes."""
        node_holder = DocumentNode()
        lines = IndexedGeneratorBuffer(self.read_str(str))
        self.parse(node_holder, lines)
        return node_holder.nodes

    def parse_file(self, path:str) -> List[ASTNode]:
        """Parses the contents of the provided file path and returns a list of ASTNodes."""
        node_holder = DocumentNode()
        lines = IndexedGeneratorBuffer(self.read_file(path))
        self.parse(node_holder, lines)
        return node_holder.nodes

    def parse_files(self, paths:Iterable[str]) -> List[ASTNode]:
        """Parses the contents of the provided file paths and returns a list of ASTNodes."""
        node_holder = DocumentNode()
        for path in paths:
            node_holder.extend(self.parse_file(path))
        return node_holder.nodes

    def parse_path(self, glob_path:str=None, recursive:bool=True) -> List[ASTNode]:
        """Parses the contents of the files matching the provided glob path and returns a list of ASTNodes."""
        node_holder = DocumentNode()
        lines = IndexedGeneratorBuffer(self.read_path(glob_path=glob_path, recursive=recursive))
        self.parse(node_holder, lines)
        return node_holder.nodes

    # TODO: Tests
    def parse_paths(self, glob_paths:Iterable[str]=None, recursive:bool=True) -> List[ASTNode]:
        """Parses the contents of the files matching the provided glob paths and returns a list of ASTNodes."""
        node_holder = DocumentNode()
        lines = IndexedGeneratorBuffer(self.read_paths(glob_paths=glob_paths, recursive=recursive))
        self.parse(node_holder, lines)
        return node_holder.nodes

    def parse_doc(self, str:str) -> DocumentNode:
        """Parses the content of the provided string and returns a DocumentNode."""
        doc = DocumentNode()
        doc.extend(self.parse_str(str))
        return doc

    def parse_doc_from_path(self, glob_path:str=None, recursive:bool=True) -> DocumentNode:
        """Parses the contents of the files matching the provided glob path and returns a DocumentNode."""
        doc = DocumentNode()
        doc.extend(self.parse_path(glob_path, recursive))
        return doc

    # TODO: Tests
    def parse_doc_from_paths(self, glob_paths:Iterable[str]=None, recursive:bool=True) -> DocumentNode:
        """Parses the contents of the files matching the provided glob paths and returns a DocumentNode."""
        doc = DocumentNode()
        doc.extend(self.parse_paths(glob_paths, recursive))
        return doc

    def read_iter(self, source:str, iter:Iterable[str]) -> Generator[SourceLine, None, None]:
        """Returns a generator that yields instances of SourceLine from the provided source and line iterator."""
        i = 0
        for line in iter:
            i = i + 1
            yield SourceLine(source, i, line.rstrip(Tokens.NEWLINE))
        yield SourceLine(source, i + 1, Tokens.EOF)

    def read_str(self, str:str) -> Generator[SourceLine, None, None]:
        """Returns a generator that yields SourceLines from the given string."""
        yield from self.read_iter('string', str.split(Tokens.NEWLINE))

    def read_file(self, path:str) -> Generator[SourceLine, None, None]:
        """Reads the given path and yields SourceLines for each line read."""
        if not os.path.exists(path):
            raise ValueError(f'File does not exist: {path}')

        with open(path) as f:
            yield from self.read_iter(path, f)

    def read_path(self, glob_path:str=None, recursive:bool=True) -> Generator[SourceLine, None, None]:
        """Reads files matching the given path and yields SourceLines for each line read."""
        for entry_path in self.list_path(glob_path=glob_path, recursive=recursive):
            if os.path.isfile(entry_path):
                yield from self.read_file(entry_path)

    # TODO: Tests
    def read_paths(self, glob_paths:Iterable[str]=None, recursive:bool=True) -> Generator[SourceLine, None, None]:
        """Reads files matching the given paths and yields SourceLines for each line read."""
        # Use the default if no paths provided:
        if glob_paths == None:
            yield from self.read_path(glob_path=None, recursive=recursive)
            return

        for glob_path in glob_paths:
            yield from self.read_path(glob_path=glob_path, recursive=recursive)

    def list_path(self, glob_path:str=None, recursive:bool=True) -> Generator[str, None, None]:
        """
        Returns a generator that yields the names of files matching the given glob pattern path.

        If a glob pattern path is not provided or if the glob pattern path resolves to a directory, 
        the following glob patterns will be attempted, and the first successful pattern will be used:

            index.wd
            **/*.wd

        Raises a ValueError if a non-directory path is specified and no files are matched.
        """
        entries = []
        if glob_path == None or os.path.isdir(glob_path):
            paths_to_try = ['index.wd', '**/*.wd']
            for path_to_try in paths_to_try:
                if glob_path == None:
                    entries = glob.glob(path_to_try, recursive=recursive)
                elif os.path.isdir(glob_path):
                    entries = glob.glob(os.path.join(glob_path, path_to_try), recursive=recursive)

                if len(entries) > 0: break
        else:
            entries = glob.glob(glob_path, recursive=recursive)

        if (len(entries) == 0) and not os.path.isdir(glob_path):
            raise ValueError(f'No files matched path {glob_path}')

        for entry in entries:
            yield os.fspath(entry)

class ActParser(Parser):
    """A parser for Writedown Act instructions."""

    def __init__(self, sequences=None):
        super().__init__(sequences)

    def parse(self, node_holder:ASTNode, lines:IndexedGeneratorBuffer, pos:int=0) -> int:
        """
        Parses @act instructions starting at the specified position in the context of the node holder.  The first line must be an @act instruction.

        Returns the (unprocessed) index from which subsequent parsing should resume, if any.
        """

        instruction_line = lines.get(pos)
        pos += 1

        number = None
        title = None

        # @act 1 Title
        match = re.match('^(\d+)?(\s*(.+))?', self.strip_instruction(instruction_line.content))
        if match:
            try:
                number = match.group(1)
                if number != None:
                    number = int(number)
            except IndexError:
                pass

            try:
                title = match.group(3)
            except IndexError:
                pass

        number = self.get_or_set_sequence(node_holder, Tokens.ACT, number)
        act = ActNode(instruction_line, number=number, title=title)
        node_holder.append(act)

        start = pos
        while lines.valid_index(pos):
            line = lines.get(pos)
            # Read until a new act:
            if self.is_instruction(line.content, Tokens.ACT):
                break
            pos += 1

        super().parse(act, lines, start, pos)

        return pos

class PartParser(Parser):
    """A parser for Writedown Part instructions."""

    def __init__(self, sequences=None):
        super().__init__(sequences)

    def parse(self, node_holder:ASTNode, lines:IndexedGeneratorBuffer, pos:int=0) -> int:
        """
        Parses @part instructions starting at the specified position in the context of the node holder.  The first line must be a @part instruction.

        Returns the (unprocessed) index from which subsequent parsing should resume, if any.
        """

        instruction_line = lines.get(pos)
        pos += 1

        number = None
        title = None

        # @part 1 Title
        match = re.match('^(\d+)?(\s*(.+))?', self.strip_instruction(instruction_line.content))
        if match:
            try:
                number = match.group(1)
                if number != None:
                    number = int(number)
            except IndexError:
                pass

            try:
                title = match.group(3)
            except IndexError:
                pass

        number = self.get_or_set_sequence(node_holder, Tokens.PART, number)
        part = PartNode(instruction_line, number=number, title=title)
        node_holder.append(part)

        start = pos
        while lines.valid_index(pos):
            line = lines.get(pos)
            # Read until a new part or an act:
            if (self.is_instruction(line.content, Tokens.PART)
                or self.is_instruction(line.content, Tokens.ACT)):
                break
            pos += 1

        super().parse(part, lines, start, pos)

        return pos 

class ChapterParser(Parser):
    """A parser for Writedown Chapter instructions."""

    def __init__(self, sequences=None):
        super().__init__(sequences)

    def parse(self, node_holder:ASTNode, lines:IndexedGeneratorBuffer, pos:int=0) -> int:
        """
        Parses @chapter instructions starting at the specified position in the context of the node holder.  The first line must be a @chapter instruction.

        Returns the (unprocessed) index from which subsequent parsing should resume, if any.
        """

        instruction_line = lines.get(pos)
        pos += 1

        number = None
        title = None

        # @chapter 1 Title
        match = re.match('^(\d+)?(\s*(.+))?', self.strip_instruction(instruction_line.content))
        if match:
            try:
                number = match.group(1)
                if number != None:
                    number = int(number)
            except IndexError:
                pass

            try:
                title = match.group(3)
            except IndexError:
                pass

        number = self.get_or_set_sequence(node_holder, Tokens.CHAPTER, number)
        chapter = ChapterNode(instruction_line, number=number, title=title)
        node_holder.append(chapter)

        start = pos
        while lines.valid_index(pos):
            line = lines.get(pos)
            # Read until a new chapter, a part, or an act:
            if (self.is_instruction(line.content, Tokens.CHAPTER)
                or self.is_instruction(line.content, Tokens.PART)
                or self.is_instruction(line.content, Tokens.ACT)):
                break
            pos += 1

        super().parse(chapter, lines, start, pos)

        return pos

class SceneParser(Parser):
    """A parser for Writedown Scene instructions."""

    def __init__(self, sequences=None):
        super().__init__(sequences)

    def parse(self, node_holder:ASTNode, lines:IndexedGeneratorBuffer, pos:int=0) -> int:
        """
        Parses @scene instructions starting at the specified position in the context of the node holder.  The first line must be a @scene instruction.

        Returns the (unprocessed) index from which subsequent parsing should resume, if any.
        """

        # TODO: Denote precondition is first line must be @scene
        instruction_line = lines.get(pos)
        pos += 1

        number = None
        title = None

        # @scene 1 Title
        match = re.match('^(\d+)?(\s*(.+))?', self.strip_instruction(instruction_line.content))
        if match:
            try:
                number = match.group(1)
                if number != None:
                    number = int(number)
            except IndexError:
                pass

            try:
                title = match.group(3)
            except IndexError:
                pass

        number = self.get_or_set_sequence(node_holder, Tokens.SCENE, number)
        scene = SceneNode(instruction_line, number=number, title=title)
        node_holder.append(scene)

        start = pos
        while lines.valid_index(pos):
            line = lines.get(pos)
            # Read until EOF, a new scene, a chapter, a part, or an act:
            if (self.is_instruction(line.content, Tokens.EOF)
                or self.is_instruction(line.content, Tokens.SCENE)
                or self.is_instruction(line.content, Tokens.CHAPTER)
                or self.is_instruction(line.content, Tokens.PART)
                or self.is_instruction(line.content, Tokens.ACT)):
                break
            pos += 1

        super().parse(scene, lines, start, pos)

        return pos

class SectionParser(Parser):
    """A parser for Writedown Section instructions."""

    def __init__(self, sequences=None):
        super().__init__(sequences)

    def parse(self, node_holder:ASTNode, lines:IndexedGeneratorBuffer, pos:int=0) -> int:
        """
        Parses @section instructions starting at the specified position in the context of the node holder.  The first line must be a @section instruction.

        Returns the (unprocessed) index from which subsequent parsing should resume, if any.
        """

        # TODO: Denote precondition is first line must be @section
        instruction_line = lines.get(pos)
        pos += 1

        number = None
        title = None

        # @section 1 Title, @section 1.1 Title
        match = re.match('^(\d[^\s]*)?(\s*(.+))?', self.strip_instruction(instruction_line.content))
        if match:
            try:
                number = match.group(1)
                if number != None:
                    try:
                        number = int(number)
                    except ValueError:
                        pass
            except IndexError:
                pass

            try:
                title = match.group(3)
            except IndexError:
                pass

        # TODO: Section number autogeneration is more complicated:
        #number = self.get_or_set_sequence(node_holder, Tokens.SECTION, number)
        section = SectionNode(instruction_line, number=number, title=title)
        node_holder.append(section)

        start = pos
        while lines.valid_index(pos):
            line = lines.get(pos)
            # Read until EOF, a new section, a chapter, a part, or an act:
            if (self.is_instruction(line.content, Tokens.EOF)
                or self.is_instruction(line.content, Tokens.SECTION)
                or self.is_instruction(line.content, Tokens.CHAPTER)
                or self.is_instruction(line.content, Tokens.PART)
                or self.is_instruction(line.content, Tokens.ACT)):
                break
            pos += 1

        super().parse(section, lines, start, pos)

        return pos

class CharacterParser(Parser):
    """A parser for Writedown Character instructions."""

    def __init__(self, sequences=None):
        super().__init__(sequences)

    def parse(self, node_holder:ASTNode, lines:IndexedGeneratorBuffer, pos:int=0) -> int:
        """
        Parses @character instructions starting at the specified position in the context of the node holder.  The first line must be a @character instruction.

        Returns the (unprocessed) index from which subsequent parsing should resume, if any.
        """

        instruction_line = lines.get(pos)
        pos += 1

        # @character name, other, names
        content = self.strip_instruction(instruction_line.content)
        names = [name.strip() for name in content.split(',')]
        name = None
        if len(names) == 0:
            # TODO: Warn
            pass
        else:
            name = names[0]
            names = names[1:]

        notes = ''
        while lines.valid_index(pos):
            line = lines.get(pos)
            # Read until any instruction:
            if self.is_instruction(line.content, Tokens.INSTRUCTION):
                break
            notes += line.content
            pos += 1

        character = CharacterNode(instruction_line, name=name, name_forms=names, notes=notes)
        node_holder.append(character)

        return pos 

class PlaceParser(Parser):
    """A parser for Writedown Place instructions."""

    def __init__(self, sequences=None):
        super().__init__(sequences)

    def parse(self, node_holder:ASTNode, lines:IndexedGeneratorBuffer, pos:int=0) -> int:
        """
        Parses @place instructions starting at the specified position in the context of the node holder.  The first line must be a @place instruction.

        Returns the (unprocessed) index from which subsequent parsing should resume, if any.
        """

        instruction_line = lines.get(pos)
        pos += 1

        # @place name, geo, geo
        content = self.strip_instruction(instruction_line.content)
        geo = [geo.strip() for geo in content.split(',')]
        name = None
        if len(geo) == 0:
            # TODO: Warn
            pass
        else:
            name = geo[0]
            geo = geo[1:]

        notes = ''
        while lines.valid_index(pos):
            line = lines.get(pos)
            # Read until any instruction:
            if self.is_instruction(line.content, Tokens.INSTRUCTION):
                break
            notes += line.content
            pos += 1

        place = PlaceNode(instruction_line, name=name, geo_paths=geo, notes=notes)
        node_holder.append(place)

        return pos            

class LocationParser(Parser):
    """A parser for Writedown Location instructions."""

    def __init__(self, sequences=None):
        super().__init__(sequences)

    def parse(self, node_holder:ASTNode, lines:IndexedGeneratorBuffer, pos:int=0) -> int:
        """
        Parses @location instructions starting at the specified position in the context of the node holder.  The first line must be a @location instruction.

        Returns the (unprocessed) index from which subsequent parsing should resume, if any.
        """

        instruction_line = lines.get(pos)
        pos += 1

        # @location name, geo, geo
        content = self.strip_instruction(instruction_line.content)
        geo = [geo.strip() for geo in content.split(',')]
        name = None
        if len(geo) == 0:
            # TODO: Warn
            pass
        else:
            name = geo[0]
            geo = geo[1:]

        content = self.strip_instruction(instruction_line.content)
        location = LocationNode(instruction_line, name=name, geo_paths=geo)
        node_holder.append(location)

        # TODO: This used to consume tokens like chapter and scene, but it's not structural so is causing issues behaving that way
        # Might be better to move out to regular parse method in main parser at this point
        """
        start = pos
        while lines.valid_index(pos):
            line = lines.get(pos)
            # Read until EOF, a new location, a scene, a chapter, a part, or an act:
            if (self.is_instruction(line.content, Tokens.EOF)
                or self.is_instruction(line.content, Tokens.LOCATION)
                or self.is_instruction(line.content, Tokens.SCENE)
                or self.is_instruction(line.content, Tokens.CHAPTER)
                or self.is_instruction(line.content, Tokens.PART)
                or self.is_instruction(line.content, Tokens.ACT)):
                break
            pos += 1

        super().parse(location, lines, start, pos)
"""

        return pos        

class SessionParser(Parser):
    """A parser for Writedown Session instructions."""

    def __init__(self, sequences=None):
        super().__init__(sequences)

    def parse(self, node_holder:ASTNode, lines:IndexedGeneratorBuffer, pos:int=0) -> int:
        """
        Do not use.

        Raises NotImplementedError.
        """
        raise NotImplementedError("Do not use")

    def get_session_node(self, instruction_line:SourceLine) -> SessionAttribute:
        """Returns a SessionAttribute parsed from the @session instruction in the given line."""

        date = None
        target = None
        name = None

        # @session 1/15/2022 1000 Name
        match = re.match('^([^\s]*)(\s+(\d+))?(\s+(.+))?', self.strip_instruction(instruction_line.content))
        if match:
            name = match.group(5)
            target = int(match.group(3)) if match.group(3) else None

            date_test = match.group(1)
            if date_test != None:
                try:
                    date = datetime.strptime(date_test, r'%m/%d/%Y').date()
                except ValueError:
                    if date_test.isnumeric():
                        target = int(date_test)
                    else:
                        name = date_test + ((' ' + name) if name else '')
        else:
            name = self.strip_instruction(instruction_line.content)

        return SessionAttribute(instruction_line, date=date, target=target, name=name)

class CommentBlockParser(Parser):
    """A parser for Writedown Comment Block instructions."""

    def __init__(self, sequences=None):
        super().__init__(sequences)

    def strip_comment_block_end(self, text):
        regex = '\\*\\@$' # TODO: Duplicates Token definition
        return re.sub(regex, '', text)

    def parse(self, node_holder:ASTNode, lines:IndexedGeneratorBuffer, pos:int=0) -> int:
        """
        Parses @* ... *@ instructions starting at the specified position in the context of the node holder.  The first line must start with a @* instruction.

        Returns the (unprocessed) index from which subsequent parsing should resume, if any.
        """

        # TODO: Denote precondition that first line must be @*
        first_line = lines.get(pos)
        pos += 1

        stop = False
        first = self.strip_instruction(first_line.content)

        # @* comment *@
        if (first.endswith(Tokens.COMMENT_BLOCK_END)):
            first = self.strip_comment_block_end(first)
            stop = True

        comments = []
        comments.append(first)

        # @* line1
        #    line2 *@
        while not stop and lines.valid_index(pos):
            line = lines.get(pos)
            pos += 1

            # Read until the end of the comment block, inclusively:
            if (line.content.endswith(Tokens.COMMENT_BLOCK_END)):
                comments.append(self.strip_comment_block_end(line.content))
                break
            else:
                comments.append(line.content)

        # Since only the first line is associated with a comment block,
        # we need to reconstitute the comment in full on this line
        # so it can be exported with the 'clean' option properly:
        first_line.content = '\n'.join(x for x in comments)

        comment = '\n'.join([x.strip() for x in comments]).strip()
        node_holder.append(CommentNode(first_line, comment=comment))

        return pos
