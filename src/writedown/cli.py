import argparse
import os
import subprocess
import sys

from colorama import init, Fore, Style

from writedown.ast import StatusNode, TextNode, TodoNode
from writedown.parser import Parser
from writedown.commands import Commands
from writedown.util import reading_time_str
from writedown.version import VERSION

class CLI():
    def __init__(self):
        self.outline_width = 60
        self.sourceline_width = 40
        self.paths = None
        """Used to track paths in shell mode"""

        init() # init colorama

    def create_argparser(self, in_shell:bool=False) -> argparse.ArgumentParser:
        argparser = argparse.ArgumentParser(prog='writedown')

        if not in_shell:
            argparser.description = 'Manage writing projects using Writedown.'
            argparser.epilog = "Run 'writedown COMMAND --help' for more information on a command"

        if in_shell:
            argparser.usage = ''

        subparsers = argparser.add_subparsers(title='commands')

        about = subparsers.add_parser('about', help='Show information about this program')
        about.set_defaults(func=self.about)

        if in_shell:
            cd = subparsers.add_parser('cd', help='(shell) Change the current project path')
            cd.add_argument('path', type=str, help='The new project path')
            cd.set_defaults(func=self.cd)

        characters = subparsers.add_parser('characters', help='Show character usage in the current project')
        characters.set_defaults(func=self.characters)

        if in_shell:
            dir = subparsers.add_parser('dir', aliases=['ls'], help='(shell) List the contents of the project path')
            dir.add_argument('path', type=str, nargs='?', help='The project path.  If not provided, defaults to the current project path.')
            dir.set_defaults(func=self.dir)

            edit = subparsers.add_parser('edit', help='(shell) Edit the contents of a path using the program defined in the EDITOR environment variable')
            edit.add_argument('path', type=str, nargs='?', help='The path.  If not provided, defaults to the current project path.')
            edit.set_defaults(func=self.edit)

        export = subparsers.add_parser('export', help='Export the current project')
        export_subparsers = export.add_subparsers()

        export_draft = export_subparsers.add_parser('draft', help='Export a draft PDF suitable for proofing')
        export_draft.add_argument('file', type=str, nargs='?', help='Output file or directory.  If filename is not provided, defaults to a file named after document title.  If directoryis not provided, defaults to the current directory.')
        export_draft.set_defaults(func=self.export_draft)

        export_text = export_subparsers.add_parser('text', help='Export a text file')
        export_text.set_defaults(func=self.export_text)

        export_pdf = export_subparsers.add_parser('pdf', help='Export a PDF')
        export_pdf.add_argument('file', type=str, nargs='?', help='Output file.  If not provided, defaults to a file named after document title.')
        export_pdf.set_defaults(func=self.export_pdf)

        export_strip = export_subparsers.add_parser('strip', help='Export a text file with all Writedown markup stripped out')
        export_strip.set_defaults(func=self.export_strip)

        export_dump = export_subparsers.add_parser('dump', help='Export a dump file for troubleshooting')
        export_dump.set_defaults(func=self.export_dump)

        info = subparsers.add_parser('info', help='Show top-level information about the current project')
        info.set_defaults(func=self.info)

        init = subparsers.add_parser('init', help='Initialize a new project in the current path')
        init_subparsers = init.add_subparsers()

        init_novel = init_subparsers.add_parser('novel', help='Initialize a project for writing novels')
        init_novel.set_defaults(func=self.init_novel)

        locations = subparsers.add_parser('locations', help='Show location usage in the current project')
        locations.set_defaults(func=self.locations)

        if in_shell:
            pwd = subparsers.add_parser('path', aliases=['pwd'], help='(shell) Show the current project paths')
            pwd.set_defaults(func=self.pwd)

        preview = subparsers.add_parser('preview', help='(shell) Shows a preview of the document')
        preview.set_defaults(func=self.preview)

        sessions = subparsers.add_parser('sessions', help='Show sessions in the current project')
        sessions.set_defaults(func=self.sessions)

        if not in_shell:
            shell = subparsers.add_parser('shell', help='Launch an interactive shell')
            shell.set_defaults(func=self.shell)

        if in_shell:
            cat = subparsers.add_parser('show', aliases=['cat'], help=f'(shell) Show the contents of a path')
            cat.add_argument('path', type=str, nargs='?', help='The path.  If not provided, defaults to the current project path.')
            cat.set_defaults(func=self.cat)

        status = subparsers.add_parser('status', help='Show statuses in the current project')
        status.set_defaults(func=self.status)

        tags = subparsers.add_parser('tags', help='Show tags in the current project')
        tags.set_defaults(func=self.tags)

        targets = subparsers.add_parser('targets', help='Show actual vs. target wordcounts in the current project')
        targets.set_defaults(func=self.targets)

        todo = subparsers.add_parser('todo', help='Show todo items in the current project')
        todo.add_argument('--context', action='store_true', help='Show context lines around todo items')
        todo.set_defaults(func=self.todo)

        wordcount = subparsers.add_parser('wordcount', aliases=['wc'], help='Show reading time, page count, wordcount, and character count statistics in the current project')
        wordcount.set_defaults(func=self.wc)

        version = subparsers.add_parser('version', help='Shows the program version')
        version.set_defaults(func=self.version)

        argparser.add_argument('-p', '--path', dest='paths', metavar='path', type=str, default=None, action='append', help='Project file or directory path.  If none is provided, defaults to the current directory.  If a directory is provided, uses Writedown file discovery logic.')

        return argparser

    def main(self):
        self.parse_args()

    def parse_args(self, input=None, in_shell=False):
        argparser = self.create_argparser(in_shell=in_shell)

        if input == None:
            args = argparser.parse_args()
        else:
            args = argparser.parse_args(input)

        default_paths = [os.getcwd()]
        try:
            if args.paths == None:
                args.paths = default_paths
        except AttributeError:
            args.paths = default_paths

        try:
            temp = args.func
        except AttributeError:
            argparser.print_help()
            return

        try:
            args.func(args)
        except (ValueError, FileNotFoundError) as err:
            print(f'{Fore.RED}{err}')
            print(Style.RESET_ALL, end='')

    def load_doc(self, args):
        parser = Parser()
        doc = parser.parse_doc_from_paths(args.paths)
        return Commands(doc)

    def blank_dash(self, value):
        return value if value else '-'

    def delta_str(self, delta):
        if delta == None: return '-'
        elif delta > 0: return '+' + str(delta)
        elif delta < 0: return str(delta)
        else: return delta

    def target_color(self, target, wordcount):
        if target != None:
            return Fore.GREEN if wordcount >= target else Fore.RED
        else:
            return None

    def indent(self, level):
        return ('--' * level) + (' ' if level > 0 else '')

    def truncate(self, text, length):
        return (text[0:length-3] + '...') if len(text) > length else text

    def row(self, *args):
        print(' '.join(args))

    def cell(self, text, width, align='left', color=None):
        text = str(text)
        if width != None:
            if len(text) > width:
                text = self.truncate(text, width)
            text = text.ljust(width) if align == 'left' else text.rjust(width)
        if color == None:
            return text
        else:
            return color + text + Style.RESET_ALL

    def shell(self, args):
        print(f'shell: {args}')
        print(Fore.GREEN + """

 __      __        .__  __             .___                 
/  \    /  \_______|__|/  |_  ____   __| _/______  _  ______
\   \/\/   /\_  __ \  \   __\/ __ \ / __ |/  _ \ \/ \/ /    \ 
 \        /  |  | \/  ||  | \  ___// /_/ (  <_> )     /   |  \ 
  \__/\  /   |__|  |__||__|  \___  >____ |\____/ \/\_/|___|  /
       \/                        \/     \/                 \/ 

                            - CLI -

                 Made with 🔥 in Cleveland, Ohio
""")
        print(Style.RESET_ALL, end='')

        print('Type "exit" to exit.\n')

        self.paths = args.paths
        while True:
            print(Style.DIM + ', '.join(self.paths) + Style.RESET_ALL + Fore.GREEN + ' writedown> ', end='')
            print(Fore.CYAN + Style.BRIGHT, end='')
            input = sys.stdin.readline()
            print(Style.RESET_ALL, end='')
            line = input.rstrip()
            if line == 'exit': break
            if line.strip(): 
                in_help = False
                show_more_help = False

                if line == 'shell':
                    continue
                elif line == 'help': 
                    command = ['-h']
                    in_help = True
                    show_more_help = True
                else: 
                    if line.startswith('help'):
                        line = ' '.join(line.split(' ')[1:]) + ' -h'
                        in_help = True

                    command = f"-p {' -p '.join(self.paths)} {line}".split(' ')

                try:
                    self.parse_args(command, in_shell=True)
                except SystemExit:
                    if in_help:
                        if show_more_help:
                            print("""
    help [command]      (shell) Show help
    exit                (shell) Exit the shell
""")
                    else:
                        print(Fore.RED + 'An error occurred processing your command.  Please check your syntax.')
                        print(Style.RESET_ALL, end='')

    def cat(self, args):
        current = args.paths
        paths = current
        if args.path:
            path = args.path
            if len(current) == 1:
                path = os.path.normpath(os.path.join(current[0], args.path))
                paths = [path]

        for path in paths:
            if os.path.isfile(path):
                with open(path) as f:
                    for line in f:
                        print(line, end='')
        print()

    def about(self, args):
        print(Fore.GREEN + f"""
 __      __        .__  __             .___                 
/  \    /  \_______|__|/  |_  ____   __| _/______  _  ______
\   \/\/   /\_  __ \  \   __\/ __ \ / __ |/  _ \ \/ \/ /    \ 
 \        /  |  | \/  ||  | \  ___// /_/ (  <_> )     /   |  \ 
  \__/\  /   |__|  |__||__|  \___  >____ |\____/ \/\_/|___|  /
       \/                        \/     \/                 \/ 

                             v{VERSION}
""" + Style.RESET_ALL)

        print(f"{Fore.CYAN}Project Website:{Style.RESET_ALL} https://github.com/cliffordoravec/writedown-parser")
        print(f"{Fore.CYAN}Writedown Language:{Style.RESET_ALL} https://github.com/cliffordoravec/writedown")
        print(f"{Fore.CYAN}Created By:{Style.RESET_ALL} Clifford Oravec")

    def cd(self, args):
        current = args.paths
        path = args.path
        if len(current) == 1:
            path = os.path.normpath(os.path.join(current[0], args.path))
        self.paths = [path]

    def characters(self, args):
        self.row(
            self.cell('', self.outline_width),
            self.cell('characters', None),
        )

        commands = self.load_doc(args)
        for (level, node, characters) in commands.characters():
            keys = list(characters.keys())
            keys.sort(key=lambda x: x.name)

            self.row(
                self.cell(self.indent(level) + node.__str__(), self.outline_width),
                self.cell(', '.join(f'{character.name} {Style.DIM}({characters[character]}){Style.NORMAL}' for character in keys), None, color=Fore.CYAN),
            )

    def dir(self, args):
        current = args.paths
        paths = current
        if args.path:
            path = args.path
            if len(current) == 1:
                path = os.path.normpath(os.path.join(current[0], args.path))
            paths = [path]

        for path in paths:
            if len(paths) > 1:
                print()
                print(f'{Style.DIM}({path}){Style.RESET_ALL}')

            effective_paths = [path for path in Parser().list_path(path)]
            working_paths = os.listdir(path) if os.path.isdir(path) else [path]
            for file in working_paths:
                full_path = os.path.join(path, file)
                effective = sum(effective_path.startswith(full_path) for effective_path in effective_paths)
                wd = file.endswith('.wd')
                print((Fore.GREEN if effective else (Fore.CYAN if wd else '')) + f'{file}{"/" if os.path.isdir(full_path) else ""}{Style.RESET_ALL}')
                if effective and os.path.isdir(full_path):
                    for effective_path in [effective_path for effective_path in effective_paths if effective_path.startswith(full_path)]:
                        print(f'  {Fore.GREEN}{Style.DIM}{effective_path[len(full_path) + 1:]}{Style.RESET_ALL}')

    def edit(self, args):
        editor = os.getenv('EDITOR')
        if not editor:
            raise ValueError('EDITOR environment variable is not defined')

        current = args.paths
        paths = current
        if args.path:
            path = args.path
            if len(current) == 1:
                path = os.path.normpath(os.path.join(current[0], args.path))
                paths = [path]

        for path in paths:
            if not os.path.isdir(path):
                subprocess.run([editor, path])

    def export_strip(self, args):
        commands = self.load_doc(args)
        for line in commands.export_strip():
            print(line)

    def export_draft(self, args):
        commands = self.load_doc(args)
        filename = f'{commands.doc.__str__()}.draft.pdf'
        if args.file == None:
            if os.path.isdir(args.paths[0]):
                args.file = os.path.join(args.paths[0], filename)
            else:
                args.file = os.path.join(os.path.dirname(args.paths[0]), filename)
        else:
            if os.path.isdir(args.file):
                args.file = os.path.join(args.file, filename)
        commands.export_draft(args.file)

    def export_dump(self, args):
        commands = self.load_doc(args)
        for (level, node) in commands.export_dump():
            self.row(
                self.cell(node.sourceinfo(level), self.sourceline_width, color=Style.DIM),
                self.cell(node.__str__(), width=None),
            )        

    def export_text(self, args):
        commands = self.load_doc(args)
        for line in commands.export_text():
            print(line)

    def export_pdf(self, args):
        commands = self.load_doc(args)
        filename = f'{commands.doc.__str__()}.pdf'
        if args.file == None:
            if os.path.isdir(args.paths[0]):
                args.file = os.path.join(args.paths[0], filename)
            else:
                args.file = os.path.join(os.path.dirname(args.paths[0]), filename)
        else:
            if os.path.isdir(args.file):
                args.file = os.path.join(args.file, filename)
        commands.export_pdf(args.file)

    def info(self, args):
        commands = self.load_doc(args)
        for line in commands.info():
            print(line)

    def init_novel(self, args):
        Commands(None).init_novel(args.paths[0])

    def locations(self, args):
        def render(location, place):
            entity = place if place else location
            return f'{f"{Fore.WHITE}{Style.DIM}" if not place else ""}{entity.name}{Style.DIM}{", " if len(entity.geo_paths) > 0 else ""}{", ".join(entity.geo_paths)}{Style.NORMAL}'

        self.row(
            self.cell('', self.outline_width),
            self.cell('locations', None),
        )

        commands = self.load_doc(args)
        for (level, node, locations) in commands.locations():
            keys = list(locations.keys())
            keys.sort(key=lambda x: x.name)

            self.row(
                self.cell(self.indent(level) + node.__str__(), self.outline_width),
                self.cell(' / '.join(render(location, locations[location]) for location in keys), None, color=Fore.CYAN),
            )

    def preview(self, args):
        commands = self.load_doc(args)
        for line in commands.export_text():
            print(line)

    def pwd(self, args):
        print(', '.join(args.paths))

    def sessions(self, args):
        self.row(
            self.cell('', self.sourceline_width),
            self.cell('', 10),
            self.cell('', 35),
            self.cell('target', 10, align='right'),
            self.cell('actual', 10, align='right'),
            self.cell('delta', 10, align='right'),
        )

        commands = self.load_doc(args)
        for map in commands.sessions():
            node = map['entry']
            target = map['target']
            wordcount = map['wordcount']
            delta = self.delta_str(map['delta'])
            color = self.target_color(target, wordcount)
            session_date = node.session.date.strftime('%m/%d/%Y') if node.session.date else ''
            session_name = node.session.name if node.session.name else ''

            self.row(
                self.cell(node.sourceinfo(), self.sourceline_width),
                self.cell(session_date, 10, color=Fore.CYAN),
                self.cell(session_name, 35),
                self.cell(self.blank_dash(target), 10, align='right', color=color),
                self.cell(wordcount, 10, align='right', color=color),
                self.cell(delta, 10, align='right', color=color),
            )

    def status(self, args):
        self.row(
            self.cell('', self.outline_width),
            self.cell('status', 10),
        )

        commands = self.load_doc(args)
        for (level, node, status) in commands.status():
            color = ''
            if status:
                match status.value:
                    case StatusNode.Statuses.NEW:
                        color = Fore.MAGENTA
                    case StatusNode.Statuses.DRAFT:
                        color = Fore.CYAN
                    case StatusNode.Statuses.REVISION:
                        color = Fore.YELLOW
                    case StatusNode.Statuses.DONE:
                        color = Fore.GREEN
            
            self.row(
                self.cell(self.indent(level) + node.__str__(), self.outline_width, color=color),
                self.cell(status.value if status else '', 10, color=color),
            )

    def tags(self, args):
        self.row(
            self.cell('', self.outline_width),
            self.cell('tags', None),
        )

        commands = self.load_doc(args)
        for (level, node, tags) in commands.tags():
            sorted = list(tags)
            sorted.sort()

            self.row(
                self.cell(self.indent(level) + node.__str__(), self.outline_width),
                self.cell(', '.join(sorted), None, color=Fore.CYAN),
            )

    def targets(self, args):
        self.row(
            self.cell('', self.outline_width),
            self.cell('target', 10, align='right'),
            self.cell('actual', 10, align='right'),
            self.cell('delta', 10, align='right'),
        )

        commands = self.load_doc(args)
        for (level, node_holder, target, wordcount, delta) in commands.targets():
            color = self.target_color(target, wordcount)
            self.row(
                self.cell(self.indent(level) + node_holder.__str__(), self.outline_width, color=color),
                self.cell(self.blank_dash(target), 10, align='right', color=color),
                self.cell(wordcount, 10, align='right', color=color),
                self.cell(self.delta_str(delta), 10, align='right', color=color),
            )

    def todo(self, args):
        commands = self.load_doc(args)
        for (level, node, context) in commands.todo(args.context):
            if context:
                self.row(
                    self.cell(node.sourceinfo(level), self.sourceline_width, color=Style.DIM),
                    self.cell(node.__str__(), self.outline_width, color=Style.DIM),
                )
            elif isinstance(node, TodoNode):
                self.row(
                    self.cell(node.sourceinfo(level), self.sourceline_width),
                    self.cell('[TODO]', 6, color=Fore.CYAN),
                    self.cell(node.text, width=None),
                )
            else:
                self.row(
                    self.cell(self.indent(level) + node.__str__(), self.outline_width),
                )

    def wc(self, args):
        self.row(
            self.cell('', self.outline_width),
            self.cell('reading time', 12, align='right'),
            self.cell('pages', 10, align='right'),
            self.cell('words', 10, align='right'),
            self.cell('chars', 10, align='right'),
        )

        commands = self.load_doc(args)
        for (level, node_holder, reading_time, pagecount, wordcount, charcount) in commands.wc():
            self.row(
                self.cell(self.indent(level) + node_holder.__str__(), self.outline_width),
                self.cell(reading_time_str(reading_time), 12, align='right'),
                self.cell(f'{pagecount:.0f}', 10, align='right'),
                self.cell(wordcount, 10, align='right'),
                self.cell(charcount, 10, align='right'),
            )

    def version(self, args):
        print(VERSION)

if __name__ == '__main__':
    instance = CLI()
    instance.main()