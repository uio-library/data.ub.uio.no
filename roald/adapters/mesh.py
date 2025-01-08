# encoding=utf-8
import isodate
import xmlwitch
import codecs
import os
import re
from lxml import etree
from ..models.resources import Concept, Collection, Label
import logging

logger = logging.getLogger(__name__)


class Mesh(object):
    """
    Class for importing legacy data from Mesh
    """

    def __init__(self, vocabulary):
        super(Mesh, self).__init__()
        self.vocabulary = vocabulary

    def load(self, filename, topnodes):
        language = self.vocabulary.default_language.alpha2
        resources = []
        ids = {}  # index lookup hash
        parents = {}
        if not os.path.isfile(filename):
            return {}

        # Topnodes
        for _, record in etree.iterparse(topnodes, tag='DescriptorRecord'):
            resource = self.process_record(record, language, parents)
            if resource is not None:
                resources.append(resource)
            record.clear()

        # First pass
        for _, record in etree.iterparse(filename, tag='DescriptorRecord'):
            resource = self.process_record(record, language, parents)
            if resource is not None:
                resources.append(resource)
            record.clear()

        # Second pass
        for res in resources:
            for notation in res.get('notation', []):
                nss = notation.split('.')
                if len(nss) > 1:
                    parent_notation = '.'.join(nss[:-1])
                else:
                    # print(notation)
                    parent_notation = notation[0]  # first letter
                if parent_notation in parents:
                    res.add('broader', parents[parent_notation])


        self.vocabulary.resources.load(resources)

    def process_record(self, record, language_code, parents):

        if record.get('DescriptorClass') == '2':
            conceptType = 'GenreForm'
        elif record.get('DescriptorClass') == '3':
            # CheckTag: IGNORE for now
            return
        elif record.get('DescriptorClass') == '4':
            conceptType = 'Geographic'
        else:
            conceptType = 'Topic'   # TODO: Perhaps 'GenreForm' if string contains ' (Form)' qualifier?

        ident = record.find('DescriptorUI').text

        obj = Concept(conceptType)
        obj.set('id', ident)

        # TODO: NLMClassificationNumber

        for node in record.xpath('./DateCreated'):
            obj.set('created', '{}-{}-{}T00:00:00Z'.format(node.find('Year').text, node.find('Month').text, node.find('Day').text))

        for node in record.xpath('./DateRevised'):
            obj.set('modified', '{}-{}-{}T00:00:00Z'.format(node.find('Year').text, node.find('Month').text, node.find('Day').text))

        for node in record.xpath('./NLMClassificationNumber'):
            obj.add('nlm', node.text)   # TODO: not converted to SKOS yet

        for node in record.xpath('./TreeNumberList/TreeNumber'):
            obj.add('notation', node.text)
            parents[node.text] = ident

        for node in record.xpath('./SeeRelatedList/SeeRelatedDescriptor/DescriptorReferredTo/DescriptorUI'):
            obj.add('related', node.text)

        concepts = record.xpath('./ConceptList/Concept')

        for node in record.findall('PublicMeSHNote'):
            obj.add('editorialNote.en', node.text.strip())

        if len(concepts) == 0:
            label = record.find('DescriptorName').find('String').text
            m = re.match('^(.+)\[(.+)\]$', label)
            obj.set('prefLabel.nb', Label(m.group(1)))
            obj.set('prefLabel.en', Label(m.group(2)))
            obj.set('isTopConcept', True)

        else:
            for concept in concepts:
                for term in concept.find('TermList').findall('Term'):
                    label = term.find('String').text
                    lang = 'en'
                    if term.find('TermUI').text.startswith('nor'):
                        lang = 'nb'
                    if concept.get('PreferredConceptYN') == 'Y' and term.get('ConceptPreferredTermYN') == 'Y':
                        logger.info('Set prefLabel.%s=%s', lang, label)
                        obj.set('prefLabel.{lang}'.format(lang=lang), Label(label))
                    else:
                        logger.info('Add altLabel.%s=%s', lang, label)
                        obj.add('altLabel.{lang}'.format(lang=lang), Label(label))

                for node in concept.findall('ScopeNote'):
                    obj.add('scopeNote.en', node.text.strip())
                for node in concept.findall('TranslatorsScopeNote'):
                    obj.add('scopeNote.nb', node.text.strip())

        return obj
