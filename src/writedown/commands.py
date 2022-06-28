import os
from typing import Dict, Iterable, List, Generator, Set, Tuple

from .ast import ASTNode, ActNode, AuthorNode, ChapterNode, CharacterNode, CommentNode, DocumentNode, LocationNode, PartNode, PlaceNode, SceneNode, SectionNode, StatusNode, TagNode, TargetNode, TextNode, TitleNode, TodoNode
from .exporters.draft import DraftExporter
from .exporters.pdf import PDFExporter
from .parser import Parser
from .util import reading_time, pagecount

class Commands():
    """Commands for processing a Writedown document."""

    def __init__(self, doc:DocumentNode):
        self.doc = doc
        """The DocumentNode."""

    def indent(self, level:int) -> str:
        """Returns a string of dashes used to indent text at the specified level."""
        return ('--' * level) + (' ' if level > 0 else '')

    def characters(self) -> Generator[Tuple[int, ASTNode, Dict[CharacterNode, int]], None, None]:
        """
        Returns a generator that, for each structural node in the current document, yields a tuple that contains:
        1. The level of the node
        2. The node itself
        3. A dictionary of all the characters occurring within the scope of the node which were defined by a Character instruction
           in the document.  The dictionary key is the CharacterNode and the value is the number of times the Character
           was referenced.

        Example:
        (3, ChapterNode, { CharacterNode: 2, CharacterNode: 3 })
        """
        character_defs = [character for character in self.doc.find(CharacterNode)]
        yield from self._characters(character_defs, self.doc, 0)

    def _characters(self, character_defs:Iterable[CharacterNode], node_holder:ASTNode, level:int) -> Generator[Tuple[int, ASTNode, Dict[CharacterNode, int]], None, None]:
        """
        Returns a generator that, for each structural node in node_holder, yields a tuple that contains:
        1. The level of the node
        2. The node itself
        3. A dictionary of all the characters occurring within the scope of the node which are defined in character_defs.
           The dictionary key is the CharacterNode and the value is the number of times the Character was referenced.

        Example:
        (3, ChapterNode, { CharacterNode: 2, CharacterNode: 3 })
        """
        def tally_push(characters:dict, character_def:CharacterNode, count:int):
            if character_def not in characters:
                characters[character_def] = 0
            characters[character_def] += count

        if node_holder.is_structural_node():
            characters = {}
            for text in node_holder.find(TextNode, recursive=node_holder.is_structural_leaf_node()):
                for character_def in character_defs:
                    if character_def.name in text.text:
                        tally_push(characters, character_def, text.text.count(character_def.name))
                    for name_form in character_def.name_forms:
                        if name_form in text.text:
                            tally_push(characters, character_def, text.text.count(name_form))
            yield ((level, node_holder, characters))

        for node in node_holder.nodes:
            yield from self._characters(character_defs, node, level + 1)        

    def export_dump(self) -> Generator[Tuple[int, ASTNode], None, None]:
        """Returns a generator that yields tuples of the form (level, node) for each node in the document."""
        yield from self._export_dump(self.doc)

    def _export_dump(self, node_holder:ASTNode, level:int=0) -> Generator[Tuple[int, ASTNode], None, None]:
        """Returns a generator that yields tuples of the form (level, node) for this node and each of its descendents."""
        yield (level, node_holder)
        for node in node_holder.nodes:
            yield from self._export_dump(node, level + 1)

    def export_draft(self, filename:None) -> bytearray:
        """Renders a draft PDF of the document to filename.  If filename is None, the raw results are returned instead."""
        return DraftExporter().export(self.doc, filename)

    def export_text(self) -> Generator[str, None, None]:
        yield from self._export_text(self.doc)

    def _export_text(self, node_holder:ASTNode) -> Generator[str, None, None]:
        match node_holder:
            case TitleNode(): yield node_holder.__str__()
            case AuthorNode(): yield node_holder.__str__()
            case ActNode(): yield '\n' + node_holder.__str__()
            case PartNode(): yield '\n' + node_holder.__str__()
            case ChapterNode(): yield '\n' + node_holder.__str__()
            case SceneNode(): yield ''
            case SectionNode(): yield '\n' + node_holder.__str__()
            case TextNode(): yield node_holder.__str__()

        for node in node_holder.nodes:
            yield from self._export_text(node)

    def export_pdf(self, filename:None) -> bytearray:
        """Renders a PDF of the document to filename.  If filename is None, the raw results are returned instead."""
        return PDFExporter().export(self.doc, filename)

    def export_strip(self) -> Generator[str, None, None]:
        yield from self._export_strip(self.doc)

    def _export_strip(self, node_holder:ASTNode) -> Generator[str, None, None]:
        yield Parser().strip_instruction(node_holder.raw)
        for node in node_holder.nodes:
            yield from self._export_strip(node)

    def info(self) -> Generator[str, None, None]:
        """Returns a generator that yields strings of human-readable summary information about the current document."""
        for node in self.doc.find(TitleNode): yield(node.__str__())
        for node in self.doc.find(AuthorNode): yield(node.__str__())

        node_types = [ActNode, PartNode, ChapterNode, SceneNode, LocationNode, SectionNode, CharacterNode, PlaceNode, TagNode, TodoNode, CommentNode]
        for node_type in node_types:
            count = sum(1 for node in self.doc.find(node_type))
            if count > 0:
                name = node_type.__name__.replace('Node', '').lower() + ('s' if count > 1 else '')
                yield f'{count} {name}'

    def init_novel(self, path:str) -> None:
        """Initializes a new project for writing a novel in the path specified."""
        if not os.path.isdir(path):
            os.mkdir(path)

        if len(os.listdir(path)) != 0:
            raise ValueError(f'{path} is not empty:  Cowardly refusing to write into non-empty directory.')

        with open(os.path.join(path, 'index.wd'), 'w') as f:
            f.write('@title Your Novel\n')
            f.write('@author Your Name\n')
            f.write('@tableofcontents\n')
            f.write('@include characters.wd\n')
            f.write('@include places.wd\n')
            f.write('@include part1/index.wd\n')

        with open (os.path.join(path, 'characters.wd'), 'w') as f:
            f.write('@character Hero')

        with open (os.path.join(path, 'places.wd'), 'w') as f:
            f.write('@place The Place')

        os.mkdir(os.path.join(path, 'part1'))

        with open(os.path.join(path, 'part1', 'index.wd'), 'w') as f:
            f.write('@part\n')
            f.write('@include ch1.wd\n')

        with open(os.path.join(path, 'part1', 'ch1.wd'), 'w') as f:
            f.write('@chapter\n')
            f.write('@scene\n')
            f.write('@location The Place\n')
            f.write('It all started when Hero walked...\n')

    def locations(self) -> Generator[Tuple[int, ASTNode, Dict[LocationNode, PlaceNode]], None, None]:
        """
        Returns a generator that, for each structural node in the current document, yields a tuple that contains:
        1. The level of the node
        2. The node itself
        3. A dictionary of the locations occurring within the scope of the node.  The dictionary key is the 
           LocationNode and the value is the resolved PlaceNode of the location if one exists in the document.

        Example:
        (3, ChapterNode, { LocationNode: None, LocationNode: PlaceNode })
        """
        place_defs = [place for place in self.doc.find(PlaceNode)]
        yield from self._locations(place_defs, self.doc, 0)

    def _locations(self, place_defs:Iterable[PlaceNode], node_holder:ASTNode, level:int) -> Generator[Tuple[int, ASTNode, Dict[LocationNode, PlaceNode]], None, None]:
        """
        Returns a generator that, for each structural node in node_holder, yields a tuple that contains:
        1. The level of the node
        2. The node itself
        3. A dictionary of the locations occurring within the scope of the node.  The dictionary key is the 
           LocationNode and the value is the resolved PlaceNode of the location if one exists in place_defs.

        Example:
        (3, ChapterNode, { CharacterNode: 2, CharacterNode: 3 })
        """
        if node_holder.is_structural_node():
            locations = {}
            for location in node_holder.find(LocationNode, recursive=node_holder.is_structural_leaf_node()):
                if location not in locations:
                    place = None
                    for place_def in place_defs:
                        #if place_def.path() == location.path():
                        if place_def.name == location.name:
                            place = place_def
                            break
                    locations[location] = place
            yield ((level, node_holder, locations))

        for node in node_holder.nodes:
            yield from self._locations(place_defs, node, level + 1)

    def sessions(self) -> Generator[dict, None, None]:
        """
        Returns a generator that yields a dictionary of the following structure for each SessionNode encountered in the document:

        {
            'session': session string representation,
            'entry': the first node the session applies to,
            'target': the session target wordcount,
            'wordcount': the actual wordcount of the session scope,
            'delta': the difference between the target and actual wordcounts
        }
        """
        yield from self._sessions(self.doc, {}, [None], 0)

    def _sessions(self, node_holder:ASTNode, map:dict, last:List[ASTNode], level:int) -> Generator[dict, None, None]:
        """
        Returns a generator that yields an aggregated dictionary of the following structure for each SessionNode encountered in 
        node_holder's hierarchy that differs from the session stored in the first element of last:

        {
            'session': session string representation,
            'entry': the first node the session applies to,
            'target': the session target wordcount,
            'wordcount': the actual wordcount of the session scope,
            'delta': the difference between the target and actual wordcounts
        }

        The first element of last is manipulated by reference to maintain and track the last session encountered.
        """
        for node in node_holder.nodes:
            if node.session:
                session = node.session.__str__()

                if not last[0]:
                    last[0] = session

                if not session in map:
                    map[session] = { 
                        'session': session, 
                        'entry': node, 
                        'target': node.session.target, 
                        'wordcount': 0,
                        'delta': 0 
                    }

                map[session]['wordcount'] += node.wordcount(False)
                map[session]['delta'] = map[session]['wordcount'] - map[session]['target'] if map[session]['target'] else None

                if last[0] != session:
                    yield map[last[0]]
                    del map[last[0]]
                    last[0] = session
            else:
                if last[0] in map:
                    yield map[last[0]]
                    del map[last[0]]
                    last[0] = None

            yield from self._sessions(node, map, last, level + 1)

        if level == 0 and last[0] in map:
            yield map[last[0]]
            del map[last[0]]

    def status(self) -> Generator[Tuple[int, ASTNode, StatusNode.Statuses], None, None]:
        """
        Returns a generator that, for each structural node in the current document, yields a tuple that contains:
        1. The level of the node
        2. The node itself
        3. The first status encountered in that node's immediate children.

        Example:
        (3, ChapterNode, StatusNode.Statuses)
        """
        yield from self._status(self.doc, 0)

    def _status(self, node_holder:ASTNode, level:int) -> Generator[Tuple[int, ASTNode, StatusNode.Statuses], None, None]:
        """
        Returns a generator that, for each structural node in node_holder, yields a tuple that contains:
        1. The level of the node
        2. The node itself
        3. The first status encountered in that node's immediate children.

        Example:
        (3, ChapterNode, StatusNode.Statuses)
        """
        if node_holder.is_structural_node():
            statuses = node_holder.find(StatusNode, recursive=False)
            status = None
            try:
                status = next(statuses).status
            except StopIteration:
                pass
            yield ((level, node_holder, status))

        for node in node_holder.nodes:
            yield from self._status(node, level + 1)

    def tags(self) -> Generator[Tuple[int, ASTNode, Set[str]], None, None]:
        """
        Returns a generator that, for each structural node in the current document, yields a tuple that contains:
        1. The level of the node
        2. The node itself
        3. A set of the tags occurring within the scope of the node

        Example:
        (3, ChapterNode, ('one', 'two'))
        """
        yield from self._tags(self.doc, 0)

    def _tags(self, node_holder:ASTNode, level:int) -> Generator[Tuple[int, ASTNode, Set[str]], None, None]:
        """
        Returns a generator that, for each structural node in node_holder, yields a tuple that contains:
        1. The level of the node
        2. The node itself
        3. A set of the tags occurring within the scope of the node

        Example:
        (3, ChapterNode, ('one', 'two'))
        """
        if node_holder.is_structural_node():
            tags = set()
            for node in node_holder.find(TagNode, recursive=node_holder.is_structural_leaf_node()):
                for tag in node.tags:
                    tags.add(tag)

            yield ((level, node_holder, tags))

        for node in node_holder.nodes:
            yield from self._tags(node, level + 1)

    def targets(self) -> Generator[Tuple[int, ASTNode, int, int, int], None, None]:
        """
        Returns a generator that, for each structural node in the current document, yields a tuple that contains:
        1. The level of the node
        2. The node itself
        3. The target wordcount
        4. The actual wordcount
        5. The delta wordcount (difference between target and actual)

        Example:
        (3, ChapterNode, 1000, 750, 250)
        """
        yield from self._targets(self.doc, 0)

    def _targets(self, node_holder:ASTNode, level:int) -> Generator[Tuple[int, ASTNode, int, int, int], None, None]:
        """
        Returns a generator that, for each structural node in node_holder, yields a tuple that contains:
        1. The level of the node
        2. The node itself
        3. The target wordcount
        4. The actual wordcount
        5. The delta wordcount (difference between target and actual)

        Example:
        (3, ChapterNode, 1000, 750, 250)
        """
        if node_holder.is_structural_node():
            target = sum(node.value for node in node_holder.find(TargetNode, recursive=node_holder.is_structural_leaf_node()))
            target = None if target == 0 else target
            wordcount = node_holder.wordcount()
            delta = wordcount - target if target else None
            yield (level, node_holder, target, wordcount, delta)

        for node in node_holder.nodes:
            yield from self._targets(node, level + 1)

    def todo(self, context:bool=False) -> Generator[Tuple[int, ASTNode, bool], None, None]:
        """
        Returns a generator that, for each TodoNode in the current document, yields a tuple that contains:
        1. The level of the node
        2. The node itself
        3. A boolean value indicating if this node is a contextual node or not

        If context is False, only TodoNodes will be yielded.
        If context is True, the node immediately preceding and the node immediately proceeding each TodoNode
        will be yielded in addition to each TodoNode.

        Examples:
        (4, TodoNode, False)

        With context set to True:
        (4, TextNode, True)
        (4, TodoNode, False)
        (4, TextNode, True)
        """
        emitted = []
        nodes = self.doc.find(TodoNode)
        for node in nodes:
            level = 0
            if not node.parent in emitted:
                parents = []
                parent = node.parent
                while parent != None:
                    parents.append(parent)
                    parent = parent.parent

                parents.reverse()
                for parent in parents:
                    if (not parent in emitted and parent.is_structural_node()):
                        yield (level, parent, False)
                        emitted.append(parent)
                    level += 1

            if context:
                index = node.parent.nodes.index(node)
                if index - 1 >= 0:
                    sibling = node.parent.nodes[index - 1]
                    yield (level, sibling, True)
                elif node.parent:
                    yield (level, parent, True)

            yield (level, node, False)

            if context:
                index = node.parent.nodes.index(node)
                if index + 1 < len(node.parent.nodes):
                    sibling = node.parent.nodes[index + 1]
                    yield (level, sibling, True)

    def wc(self) -> Generator[Tuple[int, ASTNode, Tuple[int, int, int], float, int, int], None, None]:
        """
        Returns a generator that, for each structural node in the current document, yields a tuple that contains the following
        aggregated calculations based on industry standard averages:
        1. The level of the node
        2. The node itself
        3. A tuple representing reading time (based on 275 wpm):
            1. Hours
            2. Minutes
            3. Seconds
        4. The page count (based on 300 words per page)
        5. The wordcount
        6. The character count

        Example:
        (3, ChapterNode, (0, 2, 1), 2, 555, 3127)
        """
        yield from self._wc(self.doc, 0)

    def _wc(self, node_holder:ASTNode, level:int) -> Generator[Tuple[int, ASTNode, Tuple[int, int, int], float, int, int], None, None]:
        """
        Returns a generator that, for each structural node in node_holder, yields a tuple that contains the following
        aggregated calculations based on industry standard averages:
        1. The level of the node
        2. The node itself
        3. A tuple representing reading time (based on 275 wpm):
            1. Hours
            2. Minutes
            3. Seconds
        4. The page count (based on 300 words per page)
        5. The wordcount
        6. The character count

        Example:
        (3, ChapterNode, (0, 2, 1), 2, 555, 3127)
        """
        if node_holder.is_structural_node():
            wordcount = node_holder.wordcount()
            yield (level, node_holder, reading_time(wordcount), pagecount(wordcount), wordcount, node_holder.charcount())

        for node in node_holder.nodes:
            yield from self._wc(node, level + 1)
