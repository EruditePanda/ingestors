import os
import logging
from lxml import etree

from ingestors.support.temp import TempFileSupport
from ingestors.support.shell import ShellSupport
from ingestors.support.ocr import OCRSupport

log = logging.getLogger(__name__)


class PDFSupport(ShellSupport, TempFileSupport, OCRSupport):
    """Provides helpers for PDF file context extraction."""

    #: Image ratio compared to the document size
    IMAGE_RATIO_FOR_OCR = 0.3

    def pdf_extract(self, file_path):
        """Extract pages and page text from a PDF file.

        This will convert the whole file to XML using `pdftohtml`, then run OCR
        on individual images within the file.
        """
        with self.create_temp_dir() as temp_dir:
            out_path = os.path.join(temp_dir, 'pdf.xml')
            log.debug("Converting PDF to XML...")
            self.exec_command('pdftohtml',
                              '-xml',
                              '-hidden',
                              '-q',
                              '-nodrm',
                              # '-enc', 'utf-8',
                              file_path,
                              out_path)
            self.assert_outfile(out_path)

            with open(out_path, 'r') as fh:
                xml = fh.read().decode('utf-8')
                xml = xml.replace('encoding="UTF-8"', '')
                parser = etree.XMLParser(recover=True, remove_comments=True)
                doc = etree.fromstring(xml, parser=parser)

            for page in doc.findall('./page'):
                self.pdf_extract_page(file_path, temp_dir, page)

    def pdf_alternative_extract(self, pdf_path):
        self.result.emit_pdf_alternative(pdf_path)
        self.pdf_extract(pdf_path)

    def _element_size(self, el):
        width = float(el.attrib.get('width', 1))
        height = float(el.attrib.get('height', 1))
        return width * height

    def pdf_extract_page(self, file_path, temp_dir, page):
        """Extract the contents of a single PDF page, using OCR if need be."""
        pagenum = page.get('number')
        page_size = self._element_size(page)
        is_ocr = False

        texts = []
        for text in page.findall('.//text'):
            content = text.xpath('string()').strip()
            if len(content):
                texts.append(content)

        for image in page.findall('.//image'):
            ratio = self._element_size(image) / page_size
            if len(texts) < 2 or ratio > self.IMAGE_RATIO_FOR_OCR:
                is_ocr = True

        if is_ocr and self.manager.config.get('PDF_OCR_PAGES', True):
            # log.info("Using OCR for %r, p.%s", file_path, pagenum)
            image_file = self.pdf_page_to_image(file_path, pagenum, temp_dir)
            with open(image_file, 'rb') as fh:
                text = self.extract_text_from_image(fh.read())
                if text is not None:
                    texts.append(text)

        text = '\n'.join(texts).strip()
        log.debug("Extracted %d characters of text, p.%s", len(text), pagenum)
        self.result.emit_page(int(pagenum), text)

    def pdf_page_to_image(self, file_path, pagenum, temp_dir):
        """Extract a page as an image and perform OCR.

        Used mainly because pdftohtml generated images could be really bad,
        e.g. inverted colors and weird rotations in TIFF files.
        A better idea is to make an image out of the whole page and OCR it.
        """
        out_path = os.path.join(temp_dir, '{}.pgm'.format(pagenum))

        # TODO: figure out if there's something nicer than 300dpi. Seems
        # like tesseract is trained on 300 and 600 actually sometimes gives
        # worse results.
        self.exec_command('pdftoppm',
                          '-f', str(pagenum),
                          '-singlefile',
                          '-r', '300',
                          '-gray',
                          file_path,
                          out_path.replace('.pgm', ''))
        self.assert_outfile(out_path)
        # log.debug('Extracted PDF page %r to image: %r', pagenum, out_path)
        return out_path
