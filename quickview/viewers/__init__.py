"""File viewers for QuickView."""

from quickview.viewers.base import BaseViewer
from quickview.viewers.csv_viewer import CSVViewer
from quickview.viewers.excel_viewer import ExcelViewer
from quickview.viewers.pdf_viewer import PDFViewer
from quickview.viewers.image_viewer import ImageViewer
from quickview.viewers.zip_viewer import ZipViewer
from quickview.viewers.docx_viewer import DocxViewer
from quickview.viewers.audio_viewer import AudioViewer
from quickview.viewers.text_viewer import TextViewer

__all__ = [
    "BaseViewer",
    "CSVViewer",
    "ExcelViewer",
    "PDFViewer",
    "ImageViewer",
    "ZipViewer",
    "DocxViewer",
    "AudioViewer",
    "TextViewer",
]
