from typing import Dict, Iterable, List, Generator, Set, Tuple

from fpdf import FPDF
from fpdf.enums import Align, XPos, YPos
from fpdf.outline import OutlineSection

from ..ast import ASTNode, ActNode, AuthorNode, ChapterNode, CharacterNode, CommentNode, DocumentNode, LocationNode, PageBreakNode, PartNode, PlaceNode, SceneNode, SessionAttribute, SectionNode, StatusNode, TableOfContentsNode, TagNode, TargetNode, TextNode, TitleNode, TodoNode

class WritedownPDF(FPDF):
    def set_default_font_size(self, size):
        self.default_font_size = size

    def set_doc(self, doc):
        self.doc = doc

    def header(self):
        if self.page_no() > 1:
            self.set_font("helvetica", size=10)
            self.cell(0, 10, self.doc.__str__(), align=Align.R)
            self.ln(17)
            self.set_font('DejaVu', size=self.default_font_size)

    def footer(self):
        if self.page_no() > 1:
            self.set_font("helvetica", size=10)
            self.set_y(-15)
            self.cell(0, 10, f"- {self.page_no()} -", align=Align.C, new_x=XPos.LEFT)
            self.set_font('DejaVu', size=self.default_font_size)

class PDFExporter():
    def __init__(self):
        self.output_started = False

    def export(self, doc:ASTNode, filename:None) -> bytearray:
        pdf = WritedownPDF()
        pdf.set_doc(doc)
        pdf.set_default_font_size(10)
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
        match node_holder:
            case DocumentNode(): 
                pass

            case TitleNode(): 
                if self.output_started:
                    pdf.add_page(same=True)
                text = node_holder.__str__()
                pdf.start_section(text, level)
                pdf.set_title(text)
                pdf.set_font_size(40)
                pdf.set_y(100)
                pdf.multi_cell(w=0, txt=text, align=Align.C, new_x=XPos.LEFT)
                pdf.set_font_size(pdf.default_font_size)
                pdf.ln(5)
                self.output_started = True

            case AuthorNode(): 
                text = node_holder.__str__()
                pdf.set_author(text)
                pdf.set_font_size(20)
                pdf.multi_cell(w=0, txt=text, align=Align.C)
                pdf.set_font_size(pdf.default_font_size)
                self.output_started = True

            case TableOfContentsNode():
                def render_toc(pdf:FPDF, outline:Iterable[OutlineSection]):
                    pdf.set_font_size(16)
                    pdf.multi_cell(w=0, txt='Contents', align=Align.L, new_x=XPos.LEFT)
                    pdf.ln(6)
                    pdf.set_font_size(pdf.default_font_size)
                    for section in outline:
                        if section.page_number == 1: continue
                        indent = ('    ' * section.level)
                        pdf.multi_cell(w=0, txt=f'{indent}{section.name} {("." * 10)} pg. {section.page_number}', align=Align.L, new_x=XPos.LEFT)
                        pdf.ln(3)

                pdf.add_page(same=True)
                pdf.insert_toc_placeholder(render_toc)
                self.output_started = True

            case ActNode():
                pdf.add_page(same=True)
                text = node_holder.__str__()
                pdf.start_section(text, level)
                pdf.set_font_size(32)
                pdf.set_y(100)
                pdf.multi_cell(w=0, txt=text, align=Align.C, new_x=XPos.LEFT)
                pdf.set_font_size(pdf.default_font_size)
                pdf.add_page(same=True)
                level += 1
                self.output_started = True

            case PartNode(): 
                pdf.add_page(same=True)
                text = node_holder.__str__()
                pdf.start_section(text, level)
                pdf.set_font_size(32)
                pdf.set_y(100)
                pdf.multi_cell(w=0, txt=text, align=Align.C, new_x=XPos.LEFT)
                pdf.set_font_size(pdf.default_font_size)
                level += 1
                self.output_started = True

            case ChapterNode(): 
                pdf.add_page(same=True)
                text = node_holder.__str__()
                pdf.start_section(text, level)
                pdf.set_font_size(16)
                pdf.multi_cell(w=0, txt=text, align=Align.C, new_x=XPos.LEFT)
                pdf.set_font_size(pdf.default_font_size)
                level += 1
                self.output_started = True

            case SceneNode(): 
                pdf.ln(10)
                pdf.line(pdf.get_x() + 70, pdf.get_y(), pdf.get_x() + 120, pdf.get_y())
                pdf.ln(10)
                self.output_started = True

            case SectionNode():
                text = node_holder.__str__()
                pdf.start_section(text, level)
                pdf.set_font_size(16)
                pdf.multi_cell(w=0, txt=text, align=Align.C, new_x=XPos.LEFT)
                pdf.line(pdf.get_x() + 70, pdf.get_y(), pdf.get_x() + 120, pdf.get_y())
                pdf.ln(10)
                pdf.set_font_size(pdf.default_font_size)
                level += 1
                self.output_started = True

            case TextNode():
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
                pdf.multi_cell(w=0, h=5, txt=text, align=Align.L, new_x=XPos.LEFT, markdown=True) # TODO: Make markdown option configurable
                if mono:
                    pdf.set_font("DejaVu", size=pdf.default_font_size)
                pdf.ln(3)
                self.output_started = True

            case PageBreakNode():
                pdf.add_page(same=True)

        for node in node_holder.nodes:
            self._export(pdf, node, level)
