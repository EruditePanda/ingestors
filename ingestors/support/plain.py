from normality import stringify


class PlainTextSupport(object):
    """Provides helpers for plain text context extraction."""

    def extract_plain_text_content(self, text):
        """Ingestor implementation."""
        text = stringify(text)
        self.result.emit_text_body(text)
