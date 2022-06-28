from typing import Dict, Iterable, List, Generator, Set, Tuple

from fpdf import FPDF
from fpdf.enums import Align, XPos, YPos
from fpdf.outline import OutlineSection

from ..ast import ASTNode, ActNode, AuthorNode, ChapterNode, CharacterNode, CommentNode, DocumentNode, LocationNode, PageBreakNode, PartNode, PlaceNode, SceneNode, SessionAttribute, SectionNode, StatusNode, TableOfContentsNode, TagNode, TargetNode, TextNode, TitleNode, TodoNode

class WritedownDraftPDF(FPDF):
    def set_default_font_size(self, size):
        self.default_font_size = size

    def set_doc(self, doc):
        self.doc = doc

    def set_active_sourceline(self, sourceline):
        self.active_sourceline = sourceline

    def show_lineno(self, node_holder, bar_left, bar_width):
        prev = self.get_x()
        self.set_x(bar_left)
        self.set_font(style='I')
        self.multi_cell(w=bar_width, h=10, txt=f'{node_holder.lineno}', align=Align.L, new_x=XPos.LEFT, new_y=YPos.TOP)
        self.set_x(prev)
        self.set_font(style='')

    def header(self):
        self.set_font("helvetica", size=10)
        self.cell(0, 10, 'DRAFT', align=Align.L)
        self.cell(0, 10, self.doc.__str__(), align=Align.R)
        self.ln(17)
        self.set_font('DejaVu', size=self.default_font_size)

    def footer(self):
        self.dashed_line(160, 22, 160, 280)
        self.set_font("helvetica", size=10)
        self.set_y(-15)
        self.cell(0, 10, 'DRAFT', align=Align.L, new_x=XPos.LEFT)
        self.cell(0, 10, 'DRAFT', align=Align.R, new_x=XPos.LEFT)
        self.cell(0, 10, f"- {self.page_no()} -", align=Align.C, new_x=XPos.LEFT)
        self.set_font('DejaVu', size=self.default_font_size)

class DraftExporter():
    def __init__(self):
        self.output_started = False

    def export(self, doc:ASTNode, filename:None) -> bytearray:
        pdf = WritedownDraftPDF()
        pdf.set_doc(doc)
        pdf.set_default_font_size(10)
        pdf.set_active_sourceline(None)
        pdf.add_font('DejaVu', fname='font/DejaVuSerif.ttf')
        pdf.add_font('DejaVu', fname='font/DejaVuSerif-Bold.ttf', style='B')
        pdf.add_font('DejaVu', fname='font/DejaVuSerif-Italic.ttf', style='I')
        pdf.add_font('DejaVu', fname='font/DejaVuSerif-BoldItalic.ttf', style='BI')
        pdf.set_font('DejaVu', size=pdf.default_font_size)
        pdf.add_page()
        self._export(pdf, doc, 0)
        if filename != None:
            return pdf.output(name=filename)
        else:
            return pdf.output()

    def _export(self, pdf:FPDF, node_holder:ASTNode, level:int) -> None:
        DRAFT_WIDTH = 140
        BAR_LEFT = 165
        BAR_WIDTH = 40

        if pdf.active_sourceline == None:
            pdf.set_active_sourceline(node_holder.sourceline)
            pdf.set_font(style='BIU')
            pdf.set_x(BAR_LEFT)
            pdf.multi_cell(w=BAR_WIDTH, txt=f'Source: {node_holder.source}', align=Align.L, new_x=XPos.LEFT)
            pdf.set_font(style='')
            pdf.ln(5)
        elif pdf.active_sourceline.source != node_holder.sourceline.source:
            pdf.set_active_sourceline(node_holder.sourceline)
            pdf.set_x(BAR_LEFT)
            pdf.set_font(style='BIU')
            pdf.multi_cell(w=BAR_WIDTH, txt=f'Source: {node_holder.source}', align=Align.L, new_x=XPos.LEFT)
            pdf.set_font(style='')
            pdf.ln(5)

        match node_holder:
            case DocumentNode(): 
                pass

            case TitleNode(): 
                if self.output_started:
                    pdf.add_page(same=True)
                text = node_holder.__str__()
                pdf.start_section(text, level)
                pdf.set_title(text)
                pdf.set_y(100)
                pdf.show_lineno(node_holder, BAR_LEFT, BAR_WIDTH)
                pdf.set_font_size(40)
                pdf.multi_cell(w=DRAFT_WIDTH, txt=text, align=Align.C, new_x=XPos.LEFT)
                pdf.set_font_size(pdf.default_font_size)
                pdf.ln(5)
                self.output_started = True

            case AuthorNode(): 
                text = node_holder.__str__()
                pdf.set_author(text)
                pdf.show_lineno(node_holder, BAR_LEFT, BAR_WIDTH)
                pdf.set_font_size(20)
                pdf.multi_cell(w=DRAFT_WIDTH, txt=text, align=Align.C)
                pdf.set_font_size(pdf.default_font_size)
                self.output_started = True

            case TableOfContentsNode():
                def render_toc(pdf:FPDF, outline:Iterable[OutlineSection]):
                    pdf.show_lineno(node_holder, BAR_LEFT, BAR_WIDTH)
                    pdf.set_font_size(16)
                    pdf.multi_cell(w=DRAFT_WIDTH, txt='Contents', align=Align.L, new_x=XPos.LEFT)
                    pdf.ln(6)
                    pdf.set_font_size(pdf.default_font_size)
                    for section in outline:
                        if section.page_number == 1: continue
                        indent = ('    ' * section.level)
                        pdf.multi_cell(w=DRAFT_WIDTH, txt=f'{indent}{section.name} {("." * 10)} pg. {section.page_number}', align=Align.L, new_x=XPos.LEFT)
                        pdf.ln(3)

                pdf.add_page(same=True)
                pdf.insert_toc_placeholder(render_toc)
                self.output_started = True

            case ActNode():
                pdf.add_page(same=True)
                text = node_holder.__str__()
                pdf.start_section(text, level)
                pdf.set_y(100)
                pdf.show_lineno(node_holder, BAR_LEFT, BAR_WIDTH)
                pdf.set_font_size(32)
                pdf.multi_cell(w=DRAFT_WIDTH, txt=text, align=Align.C, new_x=XPos.LEFT)
                pdf.set_font_size(pdf.default_font_size)
                pdf.add_page(same=True)
                level += 1
                self.output_started = True

            case PartNode(): 
                pdf.add_page(same=True)
                text = node_holder.__str__()
                pdf.start_section(text, level)
                pdf.set_y(100)
                pdf.show_lineno(node_holder, BAR_LEFT, BAR_WIDTH)
                pdf.set_font_size(32)
                pdf.multi_cell(w=DRAFT_WIDTH, txt=text, align=Align.C, new_x=XPos.LEFT)
                pdf.set_font_size(pdf.default_font_size)
                level += 1
                self.output_started = True

            case ChapterNode(): 
                pdf.add_page(same=True)
                text = node_holder.__str__()
                pdf.start_section(text, level)
                pdf.show_lineno(node_holder, BAR_LEFT, BAR_WIDTH)
                pdf.set_font_size(16)
                pdf.multi_cell(w=DRAFT_WIDTH, txt=text, align=Align.C, new_x=XPos.LEFT)
                pdf.set_font_size(pdf.default_font_size)
                level += 1
                self.output_started = True

            case SceneNode(): 
                pdf.ln(10)
                pdf.line(pdf.get_x() + 45, pdf.get_y(), pdf.get_x() + 95, pdf.get_y())
                pdf.ln(10)
                pdf.show_lineno(node_holder, BAR_LEFT, BAR_WIDTH)
                pdf.set_font(style='BIU')
                pdf.multi_cell(w=DRAFT_WIDTH, h=10, txt=f'{node_holder.__str__()}', align=Align.L, new_x=XPos.LEFT)
                pdf.set_font(style='')
                self.output_started = True

            case SectionNode():
                text = node_holder.__str__()
                pdf.start_section(text, level)
                pdf.show_lineno(node_holder, BAR_LEFT, BAR_WIDTH)
                pdf.set_font_size(16)
                pdf.multi_cell(w=DRAFT_WIDTH, txt=text, align=Align.C, new_x=XPos.LEFT)
                pdf.line(pdf.get_x() + 45, pdf.get_y(), pdf.get_x() + 95, pdf.get_y())
                pdf.ln(10)
                pdf.set_font_size(pdf.default_font_size)
                level += 1
                self.output_started = True

            case TextNode():
                pdf.show_lineno(node_holder, BAR_LEFT, BAR_WIDTH)
                text = node_holder.__str__()
                mono = False
                if text.startswith("\t\t"):
                    mono = True
                    pdf.set_font("courier", size=pdf.default_font_size)
                    text = text.replace('\t', (' ' * 4))
                elif text.startswith("\t"):
                    text = text.replace('\t', '')
                if not mono:
                    text = (' ' * 4) + text
                pdf.multi_cell(w=DRAFT_WIDTH, h=10, txt=text, align=Align.L, new_x=XPos.LEFT, markdown=True) # TODO: Make markdown option configurable
                if mono:
                    pdf.set_font("DejaVu", size=pdf.default_font_size)
                pdf.ln(3)
                self.output_started = True

            case CommentNode():
                pdf.show_lineno(node_holder, BAR_LEFT, BAR_WIDTH)
                pdf.set_font(style='BIU')
                pdf.set_fill_color(255, 255, 0)
                pdf.multi_cell(w=DRAFT_WIDTH, h=10, txt=f'{node_holder.__str__()}', fill=True, align=Align.L, new_x=XPos.LEFT)
                pdf.set_fill_color(0, 0, 0)
                pdf.set_font(style='')                
                self.output_started = True

            case TodoNode():
                pdf.show_lineno(node_holder, BAR_LEFT, BAR_WIDTH)
                pdf.set_font(style='BIU')
                pdf.set_text_color(255, 0, 0)
                pdf.multi_cell(w=DRAFT_WIDTH, h=10, txt=f'{node_holder.__str__()}', align=Align.L, new_x=XPos.LEFT)
                pdf.set_text_color(0, 0, 0)
                pdf.set_font(style='')
                self.output_started = True

            case LocationNode():
                pdf.show_lineno(node_holder, BAR_LEFT, BAR_WIDTH)
                pdf.set_font(style='BIU')
                pdf.multi_cell(w=DRAFT_WIDTH, h=10, txt=f'{node_holder.__str__()}', align=Align.L, new_x=XPos.LEFT)
                pdf.set_font(style='')
                self.output_started = True

            case StatusNode():
                pdf.show_lineno(node_holder, BAR_LEFT, BAR_WIDTH)
                pdf.set_font(style='BIU')
                pdf.multi_cell(w=DRAFT_WIDTH, h=10, txt=f'{node_holder.__str__()}', align=Align.L, new_x=XPos.LEFT)
                self.output_started = True

            case PageBreakNode():
                pdf.add_page(same=True)

        for node in node_holder.nodes:
            self._export(pdf, node, level)
