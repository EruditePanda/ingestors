import os
import time
import logging
import requests
import threading
from celestial import DEFAULT
from requests.exceptions import RequestException

from ingestors.exc import ConfigurationException, ProcessingException
from ingestors.util import join_path

log = logging.getLogger(__name__)


class UnoconvSupport(object):
    """Provides helpers for unconv via HTTP."""

    def get_unoconv_url(self):
        return self.manager.get_env('UNOSERVICE_URL')

    def is_unoconv_available(self):
        return self.get_unoconv_url() is not None

    @property
    def uno_client(self):
        if not hasattr(self, '_unoconv_client'):
            self._unoconv_client = threading.local()
        if not hasattr(self._unoconv_client, 'session'):
            self._unoconv_client.session = requests.Session()
        return self._unoconv_client.session

    def unoconv_to_pdf(self, file_path, temp_dir, retry=5):
        """Converts an office document to PDF."""
        if not self.is_unoconv_available():
            raise ConfigurationException("UNOSERVICE_URL is missing.")

        log.info('Converting [%s] to PDF...', self.result)
        file_name = os.path.basename(file_path)
        out_path = join_path(temp_dir, '%s.pdf' % file_name)
        try:
            with open(file_path, 'rb') as fh:
                files = {'file': (file_name, fh, DEFAULT)}
                res = self.uno_client.post(self.get_unoconv_url(),
                                           data={'format': 'pdf'},
                                           files=files,
                                           timeout=None,
                                           stream=True)
            length = 0
            with open(out_path, 'w') as fh:
                for chunk in res.iter_content(chunk_size=None):
                    length += len(chunk)
                    fh.write(chunk)

            if length == 0:
                raise ProcessingException("Could not convert to PDF.")
            return out_path
        except RequestException:
            log.exception("unoservice dead (retries: %s)", retry)
            if retry > 0:
                time.sleep(10)
                return self.unoconv_to_pdf(file_path,
                                           temp_dir,
                                           retry=retry - 1)
            raise ProcessingException("Could not convert to PDF.")
