from enum import Enum
from datetime import date
from typing import Callable, Iterator, Generator, List
import warnings

from .sourceline import SourceLine

class ASTComponent():
    """
    Represents an abstract syntax tree component.

    Contains properties and methods that other AST classes inherit from.
    """

    def __init__(self, sourceline:SourceLine):
        """Initializes a new ASTComponent instance based on the given sourceline."""

        self.sourceline = sourceline
        """The source line from which this component is constructed."""

    @property
    def source(self) -> str:
        """Returns the file path of the file that is the source of this component."""
        return self.sourceline.source

    @property
    def lineno(self) -> int:
        """Returns the line number of the file that is the source of this component."""
        return self.sourceline.lineno

    @property
    def raw(self) -> str:
        """Returns the raw contents of the file line that is the source of this component."""
        return self.sourceline.content

    def sourceinfo(self, level:int=0) -> str:
        """
        Returns a formatted information string representing the file path and 
        line number of the file that is the source of this component, indented to denote
        the level of this component in the document.

        Example:
        -- file.wd:123
        """
        return ('--' * level) + (' ' if level > 0 else '') + f'{self.source}:{self.lineno} '

class ASTAttribute(ASTComponent):
    """Represents an abstract syntax tree attribute."""

    def __init__(self, sourceline:SourceLine):
        """Initializes a new ASTAttribute instance based on the given sourceline."""
        super().__init__(sourceline)

class ASTNode(ASTComponent):
    """Represents an abstract syntax tree node."""

    def __init__(self, sourceline:SourceLine):
        """Initializes a new ASTNode instance based on the given sourceline."""

        self.parent:ASTNode = None
        """This node's parent."""

        self.nodes:List[ASTNode] = []
        """Children of this node."""

        self.session:SessionAttribute = None
        """The session this node is associated with."""

        self.session_template:SessionAttribute = None
        """
        Used to assign a child node's session when a child node is appended to this node.

        This is used during parsing to avoid assigning to or overwriting this node's session
        when this node's children belong to a session that this node does not.
        """

        super().__init__(sourceline)

    def append(self, child:'ASTNode'):
        """
        Appends child to this node's children.

        If this node has a session template defined, it will be assigned as the child node's
        session.  Otherwise, if this node has a session defined, it will be assigned as the
        child node's session.
        """
        child.parent = self
        if self.session_template:
            child.session = self.session_template
        elif self.session:
            child.session = self.session
        self.nodes.append(child)
    
    def extend(self, children:Iterator['ASTNode']):
        """Appends each of the nodes in children to this node's children."""
        for child in children:
            self.append(child)

    def filter(self, func:Callable, recursive:bool=True) -> Generator['ASTNode', None, None]:
        """
        Returns a generator of this node's descendents that func(child) returns True for. 

        If recursive is True, all descendents will be processed; if False, only this node's
        immediate children will be processed.
        """
        for child in self.nodes:
            if func(child):
                yield child
            if recursive:
                yield from child.filter(func, recursive=recursive)

    def find(self, node_type:type, recursive:bool=True) -> Generator['ASTNode', None, None]:
        """
        Returns a generator of this node's descendents that are an instance of node_type.

        If recursive is True, all descendents will be processed; if False, only this node's
        immediate children will be processed.
        """
        for child in self.nodes:
            if isinstance(child, node_type):
                yield child
            if recursive:
                yield from child.find(node_type, recursive=recursive)

    def is_structural_node(self) -> bool:
        """Returns True if the node is an instance of a structural node (DocumentNode, ActNode, PartNode, ChapterNone, SceneNode, or SectionNode) and False if not."""
        return (isinstance(self, DocumentNode)
            or isinstance(self, ActNode)
            or isinstance(self, PartNode)
            or isinstance(self, ChapterNode)
            or isinstance(self, SceneNode)
            or isinstance(self, SectionNode))

    def is_structural_leaf_node(self) -> bool:
        """Returns True if the node is the last instance of a structural node in its hierarchy and False if not."""
        if not self.is_structural_node(): return False
        try:
            next(self.filter(lambda child: child.is_structural_node))
        except StopIteration:
            return True
        return False 

    def structural_lineage(self) -> List['ASTNode']:
        """
        Returns a list of the structural nodes in this node's lineage, including this node.
        """
        lineage = []
        current = self
        while current != None:
            if current.is_structural_node():
                lineage.append(current)
            current = current.parent
        lineage.reverse()
        return lineage

    def structural_path(self) -> str:
        """
        Returns a formatted string representing this node's lineage in the form of "Grandparent > Parent > Self".
        """
        return ' > '.join(node.__str__() for node in self.structural_lineage())

    def wordcount(self, recursive:bool=True) -> int:
        """
        Returns the wordcount of all TextNodes in this node's hierarchy, including this node.

        If recursive is True, all descendents will be processed; if False, only this node
        will be processed.
        """
        if isinstance(self, TextNode): return len(self.text.split())
        if recursive:
            return sum(len(child.text.split()) for child in self.find(TextNode, recursive=recursive))
        return 0

    def charcount(self, recursive:bool=True) -> int:
        """
        Returns the character count of all TextNodes in this node's hierarchy, including this node.

        If recursive is True, all descendents will be processed; if False, only this node
        will be processed.
        """
        if isinstance(self, TextNode): return len(self.text)
        if recursive:
            return sum(len(child.text) for child in self.find(TextNode, recursive=recursive))
        return 0

class ActNode(ASTNode):
    """Represents an Act."""

    def __init__(self, sourceline:SourceLine, number:int=None, title:str=None):
        super().__init__(sourceline)
        self.number = number
        """The act number."""
        self.title = title
        """The act title."""

    def __str__(self):
        """
        Returns a string representing the act.

        Examples:
        Act 1
        Act One
        Act 1: One
        """
        number_text = f' {self.number}' if self.number else ''
        title_text = f': {self.title}' if self.title else ''
        return f'Act{number_text}{title_text}'        

class AuthorNode(ASTNode):
    """Represents an Author."""

    def __init__(self, sourceline:SourceLine, name:str=None):
        super().__init__(sourceline)
        self.name = name
        """The full author name."""

    def __str__(self):
        """
        Returns a string representing the author.

        Example:
        by Full Name
        """
        return f'by {self.name}'

class ChapterNode(ASTNode):
    """Represents a Chapter."""

    def __init__(self, sourceline:SourceLine, number:int=None, title:str=None):
        super().__init__(sourceline)
        self.number = number
        """The chapter number."""
        self.title = title
        """The chapter title."""

    def __str__(self):
        """
        Returns a string representing the chapter.

        Examples:
        Chapter 1
        Chapter One
        Chapter 1: One
        """
        number_text = f' {self.number}' if self.number else ''
        title_text = f': {self.title}' if self.title else ''
        return f'Chapter{number_text}{title_text}'

class CharacterNode(ASTNode):
    """Represents a Character."""

    def __init__(self, sourceline:SourceLine, name:str, name_forms:Iterator[str]=None, notes:str=None):
        super().__init__(sourceline)
        self.name = name
        """The main character name."""
        self.name_forms = name_forms if name_forms != None else []
        """Alternative character names."""
        self.notes = notes
        """Notes about the character."""

    def __str__(self):
        """
        Returns a string representing the character.

        Examples:
        Character: Main Name
        Character: Main Name (Alternate Name, Another Name)
        """
        return f'Character: {self.name}' + (f'({", ".join(self.name_forms)})' if self.name_forms else '')

class CommentNode(ASTNode):
    """Represents a Comment."""

    def __init__(self, sourceline:SourceLine, comment:str=None):
        super().__init__(sourceline)
        self.comment = comment
        """The comment."""

    def __str__(self):
        """
        Returns a string representing the comment.

        Example:
        Comment: The Comment
        """
        return f'Comment: {self.comment}'
    
class DocumentNode(ASTNode):
    """Represents a Document."""

    def __init__(self):
        super().__init__(SourceLine('document', 0, ''))
                
    def __str__(self):
        """
        Returns a string representing the document.  If a TitleNode is defined in the hierarchy, 
        it will be used as the string representation.  Otherwise, "Document" will be used.

        Examples:
        Title
        Document
        """
        title = ''.join([title.text for title in self.find(TitleNode)])
        return title if title else 'Document'

class LocationNode(ASTNode):
    """Represents a Location."""

    def __init__(self, sourceline:SourceLine, name:str=None, geo_paths:Iterator[str]=None):
        super().__init__(sourceline)
        self.name = name
        """The main location name."""
        self.geo_paths = geo_paths if geo_paths != None else []
        """Additional geographic paths for the location."""

    def __str__(self):
        """
        Returns a string representation of the location based on the path().

        Examples:
        Location: Main Location Name
        Location: Main Location Name, Geo 1 Name, Geo 2 Name
        """
        return f'Location: {self.path()}'

    def path(self):
        """
        Returns a string representing the full path of the location.

        Examples:
        Main Location Name
        Main Location Name, Geo 1 Name, Geo 2 Name
        """
        return f'{self.name}{", " if len(self.geo_paths) > 0 else ""}{", ".join(self.geo_paths)}'

class PageBreakNode(ASTNode):
    """Represents a placeholder for a page break."""

    def __init__(self, sourceline:SourceLine):
        super().__init__(sourceline)

    def __str__(self):
        """
        Returns a string representing the placeholder.

        Example:
        [PAGEBREAK]
        """
        return f'[PAGEBREAK]'

class PartNode(ASTNode):
    """Represents a Part."""

    def __init__(self, sourceline:SourceLine, number:int=None, title:str=None):
        super().__init__(sourceline)
        self.number = number
        """The part number."""
        self.title = title
        """The part title."""

    def __str__(self):
        """
        Returns a string representing the part.

        Examples:
        Part 1
        Part One
        Part 1: One
        """
        number_text = f' {self.number}' if self.number else ''
        title_text = f': {self.title}' if self.title else ''
        return f'Part{number_text}{title_text}'        

class PlaceNode(ASTNode):
    """Represents a Place."""

    def __init__(self, sourceline:SourceLine, name:str=None, geo_paths:Iterator[str]=None, notes:str=None):
        super().__init__(sourceline)
        self.name = name
        """The main place name."""
        self.geo_paths = geo_paths if geo_paths != None else []
        """Additional geographic paths for the place."""
        self.notes = notes
        """"Notes about the place."""

    def __str__(self):
        """
        Returns a string representation of the place based on the path().

        Examples:
        Place: Main Place Name
        Place: Main Place Name, Geo 1 Name, Geo 2 Name
        """
        return f'Place: {self.path()}'

    def path(self):
        """
        Returns a string representing the full path of the place.

        Examples:
        Main Place Name
        Main Place Name, Geo 1 Name, Geo 2 Name
        """        
        return f'{self.name}{", " if len(self.geo_paths) > 0 else ""}{", ".join(self.geo_paths)}'

class SceneNode(ASTNode):
    """Represents a Scene."""

    def __init__(self, sourceline:SourceLine, number:int=None, title:str=None):
        super().__init__(sourceline)
        self.number = number
        """The scene number."""
        self.title = title
        """The scene title."""

    def __str__(self):
        """
        Returns a string representation of the scene.

        Examples:
        Scene 1
        Scene One
        Scene 1: One
        """
        number_text = f' {self.number}' if self.number else ''
        title_text = f': {self.title}' if self.title else ''
        return f'Scene{number_text}{title_text}'

class SectionNode(ASTNode):
    """Represents a Section."""

    def __init__(self, sourceline:SourceLine, number:str=None, title:str=None):
        super().__init__(sourceline)
        self.number = number
        """The section number."""
        self.title = title
        """The section title."""

    def __str__(self):
        """
        Returns a string representation of the section.

        Examples:
        Section 1
        Section One
        Section 1: One
        """
        number_text = f' {self.number}' if self.number else ''
        title_text = f': {self.title}' if self.title else ''
        return f'Section{number_text}{title_text}'        

class SessionAttribute(ASTAttribute):
    """Represents a Session."""

    def __init__(self, sourceline:SourceLine, date:date, target:int, name:str):
        super().__init__(sourceline)
        self.date = date
        """The session date."""
        self.target = target
        """The session target wordcount."""
        self.name = name
        """The session name."""

    def __str__(self):
        """
        Returns a string representing the session.

        Examples:
        Session 5/20/2022
        Session At the park
        Session 5/20/2022 At the park
        """
        date_text = f' {self.date.strftime("%m/%d/%Y")}' if self.date else ''
        name_text = f' {self.name}' if self.name else ''
        return f'Session{date_text}{name_text}'

class StatusNode(ASTNode):
    """Represents the Status of a structural node."""

    class Statuses(str, Enum):
        """Enumeration of valid statuses."""
        NEW = 'new'
        """Indicates that the associated section is new."""
        DRAFT = 'draft'
        """Indicates that the associated section is a draft."""
        REVISION = 'revision'
        """Indicates that the associated section is a revision."""
        DONE = 'done'
        """Indicates that the associated section is done."""

    def __init__(self, sourceline:SourceLine, status:str):
        super().__init__(sourceline)
        self.status = StatusNode.Statuses(status)
        """The status."""

    def __str__(self):
        """
        Returns a string representation of the status.

        Examples:
        Status: new
        Status: draft
        Status: revision
        Status: done
        """
        return f'Status: {self.status.value}'

class TagNode(ASTNode):
    """Represents a Tag."""

    def __init__(self, sourceline:SourceLine, tags:List[str]):
        super().__init__(sourceline)
        self.tags = tags
        """The tags."""

    def __str__(self):
        """
        Returns a string representation of the associated tags.

        Examples:
        Tags: tag
        Tags: one, two
        """
        return f'Tags: {", ".join(self.tags)}'

class TableOfContentsNode(ASTNode):
    """Represents a placeholder for a table of contents."""

    def __init__(self, sourceline:SourceLine):
        super().__init__(sourceline)

    def __str__(self):
        """
        Returns a string representation of the placeholder.

        Example:
        [TABLEOFCONTENTS]
        """
        return f'[TABLEOFCONTENTS]'

class TargetNode(ASTNode):
    """Represents a target wordcount for a structural node."""

    def __init__(self, sourceline:SourceLine, value:int):
        super().__init__(sourceline)
        self.value = value
        """The target wordcount."""

    def __str__(self):
        """
        Returns a string representation of the target.

        Example:
        Target: 1000 words
        """
        return f'Target: {self.value} words'

class TextNode(ASTNode):
    """Represents standard text."""

    def __init__(self, sourceline:SourceLine, text:str):
        super().__init__(sourceline)
        self.text = text
        """The text."""

    def __str__(self):
        """Returns the text."""
        return f'{self.text}'

class TitleNode(ASTNode):
    """Represents the Title."""

    def __init__(self, sourceline:SourceLine, text:str):
        super().__init__(sourceline)
        self.text = text
        """The title text."""

    def __str__(self):
        """Returns the title."""
        return f'{self.text}'

class TodoNode(ASTNode):
    """Represents a todo."""

    def __init__(self, sourceline:SourceLine, text:str):
        super().__init__(sourceline)
        self.text = text
        """The todo text."""

    def __str__(self):
        """
        Returns a string representation of the todo.

        Example:
        TODO: Do this thing
        """
        return f'TODO: {self.text}'

class UnmappedInstructionNode(ASTNode):
    """
    Represents an unmapped instruction.
    
    An unmapped instruction is any Writedown instruction not explicitly supported by the parser.
    For example, if the input contained the instruction @notaninstruction, that would be
    considered an unmapped instruction. 

    This feature exists to allow third party instructions to occur within input
    that can be processed by third party tooling.
    """

    def __init__(self, sourceline:SourceLine, instruction:str=None, text:str=None):
        super().__init__(sourceline)
        self.instruction = instruction
        """The unmapped instruction.  For example: @notaninstruction"""
        self.text = text
        """Any text following the unmapped instruction."""

    def __str__(self):
        """
        Returns a string representation of the unmapped instruction.

        Example:
        [NOTMAPPED] @notaninstruction Trailing text
        """
        return f'[NOTMAPPED] {self.instruction} {self.text}'