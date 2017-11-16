from ingestors.base import Ingestor
from ingestors.support.soffice import LibreOfficeSupport
from ingestors.support.opendoc import OpenDocumentSupport


class OpenDocumentIngestor(Ingestor, LibreOfficeSupport, OpenDocumentSupport):
    """Office/Word document ingestor class.

    Converts the document to PDF and extracts the text.
    Mostly a slightly adjusted PDF ingestor.

    Requires system tools:

    - Open/Libre Office with dependencies
    - image ingestor dependencies to cover any embeded images OCR

    """

    MIME_TYPES = [
        'application/vnd.oasis.opendocument.text',
        'application/vnd.oasis.opendocument.text-template',
        'application/vnd.oasis.opendocument.presentation',
        'application/vnd.oasis.opendocument.graphics',
        'application/vnd.oasis.opendocument.graphics-template',
        'application/vnd.oasis.opendocument.presentation-template',
        'application/vnd.oasis.opendocument.chart',
        'application/vnd.oasis.opendocument.chart-template',
        'application/vnd.oasis.opendocument.image',
        'application/vnd.oasis.opendocument.image-template',
        'application/vnd.oasis.opendocument.formula',
        'application/vnd.oasis.opendocument.formula-template',
        'application/vnd.oasis.opendocument.text-master',
        'application/vnd.oasis.opendocument.text-web',
    ]
    EXTENSIONS = ['odt', 'odp', 'otp']
    SCORE = 5

    def ingest(self, file_path):
        """Ingestor implementation."""
        self.parse_opendocument(file_path)
        with self.create_temp_dir() as temp_dir:
            pdf_path = self.document_to_pdf(file_path, temp_dir)
            self.pdf_alternative_extract(pdf_path)
