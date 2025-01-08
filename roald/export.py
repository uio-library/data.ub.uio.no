import os.path
import logging

logger = logging.getLogger(__name__)


class PreparedExport(object):

    def __init__(self, model):
        self.model = model
        self.prepared_data = self.model.prepare()

    def write(self, filename, **kwargs):
        for k, v in self.prepared_data.items():
            kwargs[k] = v
        filename = os.path.expanduser(filename)
        with open(filename, 'wb') as f:
            f.write(self.model.serialize(**kwargs))
        logger.info('Export to {} complete'.format(filename))
