# encoding=utf-8
import codecs
import json
import os
from iso639 import languages
import logging
import requests
import traceback

from .adapters import Mesh
from .adapters import Bibsys
from .adapters import Roald2
from .adapters import Roald3
from .adapters import Marc21
from .adapters import Skos
from .models import Vocabulary
from .export import PreparedExport

logger = logging.getLogger(__name__)


class Mailer:
    def __init__(self, config):
        self.config = config
        self.config['reply'] = self.config['reply'] if 'reply' in self.config else self.config['sender']
    
    def send(self, subject, body):
        if self.config is None:
            logger.info('Mail not configured')
        else:
            data = {"err":body,"secret":"ipoargb6098538956951847123919238590870"}

            resp = requests.post('https://data.ub.uio.no/sendErrorMsgByMail.php', params=data)

            #requests.post(
            #    "https://api.mailgun.net/v3/%(domain)s/messages" % self.config,
            #    auth=("api", self.config['apikey']),
            #    data={"from": self.config['sender'],
            #        "h:Reply-To": self.config['reply'],
            #        "to": self.config['recipients'],
            #        "subject": subject,
            #        "text": body,
            #    }
            #)        


class Roald(object):
    """
    Roald

    Example:

    >>> roald = roald.Roald()
    >>> roald.load('./data/', format='roald2', language='nb')
    >>> roald.set_uri_format('http://data.ub.uio.no/realfagstermer/c{id}')
    >>> roald.save('realfagstermer.json')
    >>> roald.export('realfagstermer.marc21.xml', format='marc21')
    """

    def __init__(self, mail_config=None):
        super(Roald, self).__init__()
        self.vocabulary = Vocabulary()
        self.default_language = None
        if mail_config is not None:
            self.mailer = Mailer(mail_config)
        else:
            self.mailer = None

    def load(self, filename, format='roald3', language=None, **kwargs):
        """
            - filename : the filename to a 'roald3' file or path to a 'roald2' directory.
            - format : 'roald3', 'roald2' or 'bibsys'.
            - language : language code (only for 'roald2')
        """
        filename = os.path.expanduser(filename)
        if format == 'roald3':
            if language is not None:
                logger.warn('roald.load: Setting language has no effect when loading Roald3 data')
            Roald3(self.vocabulary).load(filename)
        elif format == 'roald2':
            self.vocabulary.default_language = languages.get(alpha2=language)
            Roald2(self.vocabulary).load(filename)
        elif format == 'bibsys':
            self.vocabulary.default_language = languages.get(alpha2=language)
            Bibsys(self.vocabulary).load(filename, **kwargs)
        elif format == 'mesh':
            self.vocabulary.default_language = languages.get(alpha2=language)
            Mesh(self.vocabulary).load(filename, **kwargs)
        elif format == 'skos':
            Skos(self.vocabulary).load(filename)
        elif format == 'marc21':
            self.vocabulary.default_language = languages.get(alpha2=language)
            try:
                Marc21(self.vocabulary, mailer=self.mailer).load(filename, **kwargs)
            except Exception as error:
                if self.mailer is not None:
                    err_str = '<br>'.join(traceback.format_exception(type(error), error, error.__traceback__))
                    hline = '<br>-----------------------------------------------------<br>'
    #                self.mailer.send(
    #                    'Eksport av %s feila' % filename,
    #                    'Følgende problem oppsto:' + hline + str(error),
    #                    '(XP) Utvidet feilrapportering:' + str(err_str) + hline
    #                )
                    self.mailer.send(
                        'Feil under import av %s' % filename,
                        "<br>Rapport:<br>" + str(error) + hline + "<br>"
                    )
                    quit
                    raise Exception("Errors occured during import. Mail sent.")
                raise error
        else:
            raise ValueError('Unknown format')

        logger.info('Loaded {} resources'.format(len(self.vocabulary.resources)))

    def set_uri_format(self, value, prefix=''):
        self.vocabulary.uri_format = value
        self.vocabulary.id_prefix = prefix

    def save(self, filename):
        filename = os.path.expanduser(filename)

        Roald3(self.vocabulary).save(filename)

        logger.info('Saved {} resources to {}'.format(len(self.vocabulary.resources), filename))

    def prepare_export(self, format, **kwargs):
        if format == 'marc21':
            logger.info('Preparing MARC21 export')
            model = Marc21(self.vocabulary, **kwargs)
        elif format == 'rdfskos':
            logger.info('Preparing RDF/SKOS export')
            model = Skos(self.vocabulary, **kwargs)
        else:
            raise Exception('Unknown format')
        return PreparedExport(model)

    def export(self, filename, format, **kwargs):
        try:
            prepared = self.prepare_export(format, **kwargs)
            prepared.write(filename)
        except Exception as error:
            if self.mailer is not None:
                err_str = '<br>'.join(traceback.format_exception(type(error), error, error.__traceback__))
                hline = '<br>-----------------------------------------------------<br>'
#                self.mailer.send(
#                    'Eksport av %s feila' % filename,
#                    'Følgende problem oppsto:' + hline + str(error),
#                    '(XP) Utvidet feilrapportering:' + str(err_str) + hline
#                )
                self.mailer.send(
                    'Feil under eksport av %s' % filename,
                    "<br>Rapport:<br>" + str(err_str) + hline + str(error) + "<br><br>" 
                )

                raise Exception("Errors occured during import. Mail sent.")
            raise error

    def authorize(self, value):
        # <value> can take a compound heading value like "$a Component1 $x Component2 $x Component3"
        return self.concepts.get(term=value)
        # parts = [[x.strip()[0], x.strip()[1:].strip()] for x in value.split('$') if len(x.strip()) > 0]
        # for part in parts:
