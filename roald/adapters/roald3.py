import json
import re
import codecs
from iso639 import languages


class Roald3(object):

    def __init__(self, vocabulary):
        super(Roald3, self).__init__()
        self.vocabulary = vocabulary

    def normalize_line_endings(self, txt):
        # Normalize to unix line endings
        return txt.replace('\r\n','\n').replace('\r','\n')

    def load(self, filename):
        data = json.load(codecs.open(filename, 'r', 'utf-8'))

        if 'uri_format' in data:
            self.vocabulary.uri_format = data['uri_format']

        if 'default_language' in data:
            self.vocabulary.default_language = languages.get(alpha2=data['default_language'])

        if 'resources' in data:
            self.vocabulary.resources.load(data['resources'])

    def save(self, filename):

        if self.vocabulary.default_language is None:
            raise RuntimeError('vocabulary.save: No default language code set.')

        data = {
            'default_language': self.vocabulary.default_language.alpha2,
            'uri_format': self.vocabulary.uri_format,
            'resources': self.vocabulary.resources.serialize()
        }

        jsondump = json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False)

        # Remove trailling spaces (https://bugs.python.org/issue16333)
        jsondump = re.sub('\s+$', '', jsondump, flags=re.MULTILINE)

        # Normalize to unix line endings
        jsondump = self.normalize_line_endings(jsondump)

        with open(filename, 'wb') as stream:
            stream.write(jsondump.encode('utf-8'))
