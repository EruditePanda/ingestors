import os
import six
import magic
import logging
import hashlib
from normality import stringify
from pkg_resources import iter_entry_points

from ingestors.result import Result
from ingestors.directory import DirectoryIngestor
from ingestors.exc import ProcessingException
from ingestors.util import normalize_mime_type

log = logging.getLogger(__name__)


class Manager(object):
    """Handles the lifecycle of an ingestor. This can be subclassed to embed it
    into a larger processing framework."""

    RESULT_CLASS = Result
    MAGIC = magic.Magic(mime=True)

    def __init__(self, config):
        self.config = config

    def get_env(self, name, default=None):
        """Get configuration from local config or environment."""
        value = stringify(self.config.get(name))
        if value is not None:
            return value
        value = stringify(os.environ.get(name))
        if value is not None:
            return value
        return default

    @property
    def ingestors(self):
        if not hasattr(self, '_ingestors'):
            self._ingestors = []
            for ep in iter_entry_points('ingestors'):
                self._ingestors.append(ep.load())
        return self._ingestors

    def auction(self, file_path, result):
        if os.path.isdir(file_path):
            result.mime_type = DirectoryIngestor.MIME_TYPE
            return DirectoryIngestor

        if result.mime_type is None:
            mime_type = self.MAGIC.from_file(file_path)
            result.mime_type = normalize_mime_type(mime_type)

        best_score, best_cls = 0, None
        for cls in self.ingestors:
            score = cls.match(file_path, mime_type=result.mime_type)
            if score > best_score:
                best_score = score
                best_cls = cls

        if best_cls is None:
            raise ProcessingException("Format not supported: %r (%s)" %
                                      (file_path, result.mime_type))
        return best_cls

    def before(self, result):
        """Callback called before the processing starts."""
        pass

    def after(self, result):
        """Callback called after the processing starts."""
        pass

    def handle_child(self, parent, file_path, **kwargs):
        result = self.RESULT_CLASS(file_path=file_path, **kwargs)
        parent.children.append(result)
        self.ingest(file_path, result=result)

    def checksum_file(self, result, file_path):
        "Generate a hash and file size for a given file name."
        if os.path.isdir(file_path):
            return

        if result.checksum is not None and result.size is not None:
            return

        checksum = hashlib.sha1()
        size = 0
        with open(file_path, 'rb') as fh:
            while True:
                block = fh.read(8192)
                if not block:
                    break
                size += len(block)
                checksum.update(block)

        result.checksum = checksum.hexdigest()
        result.size = size

    def ingest(self, file_path, result=None, ingestor_class=None):
        """Main execution step of an ingestor."""
        if result is None:
            result = self.RESULT_CLASS(file_path=file_path)

        self.checksum_file(result, file_path)
        self.before(result)
        try:
            if ingestor_class is None:
                ingestor_class = self.auction(file_path, result)
                log.debug("Ingestor [%s, %s]: %s", result.label,
                          result.mime_type, ingestor_class.__name__)
            self.delegate(ingestor_class, result, file_path)
            result.status = Result.STATUS_SUCCESS
        except ProcessingException as pexc:
            result.error_message = six.text_type(pexc)
            result.status = Result.STATUS_FAILURE
        except Exception as exception:
            log.exception(exception)
            result.status = Result.STATUS_STOPPED
        finally:
            self.after(result)

        return result

    def delegate(self, ingestor_class, result, file_path):
        ingestor = ingestor_class(self, result)
        ingestor.ingest(file_path)
