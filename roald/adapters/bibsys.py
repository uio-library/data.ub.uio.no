# encoding=utf-8
import isodate
import xmlwitch
import codecs
import os
import re
from lxml import etree
from ..models.resources import Concept, Collection, Label
from ..util import AlreadyExists
import logging

logger = logging.getLogger(__name__)


class Bibsys(object):
    """
    Class for importing legacy data from Bibsys
    """

    encoding = 'latin1'
    vocabulary = None

    def __init__(self, vocabulary):
        super(Bibsys, self).__init__()
        self.vocabulary = vocabulary

    def load(self, filename, exclude_underemne=False):
        language = self.vocabulary.default_language.alpha2
        self.exclude_underemne = exclude_underemne
        resources = []
        ids = {}  # index lookup hash
        terms = {}  # term lookup hash
        uf_terms = {}  # term lookup hash
        parents = {}
        if not os.path.isfile(filename):
            return {}

        # First pass
        for _, record in etree.iterparse(filename, tag='post'):
            resource = self.process_record(record, language, parents)
            if resource is not None:
                resources.append(resource)
                ids[resource['id']] = len(resources) - 1
                terms[resource.get('prefLabel.nb').value] = len(resources) - 1
            record.clear()

        # Second pass
        for _, record in etree.iterparse(filename, tag='post'):
            resource = self.process_relations(record, resources, ids, language, parents)
            if resource is not None:
                for term in resource.get('altLabel.nb', []):
                    uf_terms[term.value] = len(resources) - 1
            record.clear()

        print('Found %d uf_terms' % len(uf_terms.keys()))

        # Third pass
        for _, record in etree.iterparse(filename, tag='post'):
            resource = self.process_second_level_relations(record, resources, ids, terms, uf_terms)
            record.clear()


        self.vocabulary.resources.load(resources)
        logger.info('Loaded %d concepts from %s', len(resources), filename)

    def get_label(self, record):
        label = record.find('hovedemnefrase').text
        kv = record.find('kvalifikator')
        if kv is not None:
            label = u'{} ({})'.format(label, kv.text)
        if not self.exclude_underemne:
            for uf in record.findall('underemnefrase'):
                label = u'{} - {}'.format(label, uf.text)
        for node in record.findall('kjede'):
            label = u'{} : {}'.format(label, node.text)
        return label

    def process_record(self, record, language, parents):

        conceptType = 'Topic'

        if record.find('se-id') is not None:  # We'll handle those in the second pass
            return

        ident = record.find('term-id').text
        if record.find('type') is not None:
            record_type = record.find('type').text.upper()
        else:
            record_type = 'Topic'

        if record.find('gen-se-henvisning') is not None:
            obj = Concept('SplitNonPreferredTerm')

        elif record_type == 'F':
            obj = Collection()

        elif record_type == 'K':
            obj = Concept('LinkingTerm')

        elif record_type == 'T':
            obj = Concept('Temporal')

        elif record_type == 'G':
            obj = Concept('Geographic')

        else:
            obj = Concept(conceptType)

        obj.set('id', ident)

        for node in record.findall('signatur'):
            obj.add('notation', node.text)

        for node in record.findall('klass-signatur/signatur'):
            obj.add('notation', node.text)

        for node in record.findall('toppterm-id'):
            if node.text == ident:
                obj.set('isTopConcept', True)

        if not obj.get('isTopConcept') is True:
            for node in record.findall('overordnetterm-id') + record.findall('ox-id'):
                parents[ident] = parents.get(ident, []) + [node.text]

        prefLabel = self.get_label(record)
        if isinstance(obj, Concept) and prefLabel.endswith('(Form)'):
            obj.set_type('GenreForm')
            prefLabel = prefLabel[:-7]
        obj.set('prefLabel.{}'.format(language), Label(prefLabel))

        dato = record.find('dato').text
        obj.set('modified', '{}T00:00:00Z'.format(dato))

        for node in record.findall('definisjon'):
            obj.set('definition.{}'.format(language), node.text)

        for node in record.findall('gen-se-ogsa-henvisning'):
            obj.add('scopeNote.{}'.format(language), u'Se også: {}'.format(node.text))

        for node in record.findall('noter'):
            # Ihvertfall i Humord virker disse temmelig interne... Mulig noen kan flyttes til scopeNote
            obj.add('editorialNote', node.text)

        for node in record.findall('lukket-bemerkning'):
            obj.add('editorialNote', u'Lukket bemerkning: {}'.format(node.text))

        return obj

    def get_parents(self, parents, resources, ids, tid):
        out = []
        # if parents.get(tid) is None:
        #     logger.warn('No parents for %s', tid)
        for parent_id in parents.get(tid, []):
            if parent_id not in ids:
                logger.warn('The parent ID %s of %s is not a Concept or a Collection', parent_id, tid)
            elif isinstance(resources[ids[parent_id]], Concept):
                out.append(resources[ids[parent_id]])
            else:
                x = self.get_parents(parents, resources, ids, parent_id)
                out.extend(x)
        return out

    def process_relations(self, record, resources, ids, language, parents):

        tid = record.find('term-id').text

        if record.find('se-id') is not None:
            se_id = record.find('se-id').text
            label_val = self.get_label(record)
            try:
                other_res = resources[ids[se_id]]
                if label_val.find(' [eng1]') != -1:
                    label_val = label_val.replace(' [eng1]', '')
                    try:
                        other_res.set('prefLabel.en', Label(label_val))
                    except AlreadyExists:
                        logger.warn('%s already had a preferred term (en), adding "%s" as alternative term instead',
                                    se_id, label_val)
                        other_res.add('altLabel.en', Label(label_val))

                elif label_val.find(' [eng]') != -1:
                    label_val = label_val.replace(' [eng]', '')
                    other_res.add('altLabel.en', Label(label_val))
                else:
                    other_res.add('altLabel.{}'.format(language), Label(label_val))
                return other_res
            except KeyError:
                logger.warn('Cannot add "%s" as an alternative term to %s because the latter doesn\'t exist as a concept (it might be a term though)', label_val, se_id)
            return

        resource = resources[ids[tid]]

        for node in record.findall('se-ogsa-id'):
            try:
                related = resources[ids[node.text]]
                if isinstance(related, Collection):
                    logger.warn(u'Relation <%s %s> RT <%s %s>, where the latter is a collection, is not allowed in SKOS',
                                tid, resource.get('prefLabel.nb').value, related.id, related.get('prefLabel.nb').value)
                    resource.add('related', related['id'])
                else:
                    resource.add('related', related['id'])
            except KeyError:
                logger.warn('Cannot convert relation <%s %s> RT <%s> because the latter is not a preferred term of any concept (it might be a non-preferred term though)',
                            tid, resource.get('prefLabel.nb').value, node.text)

        # Add normal hierarchical relations
        if isinstance(resource, Concept) and not resource.get('isTopConcept') is True:
            for parent in self.get_parents(parents, resources, ids, tid):
                resource.add('broader', parent['id'])

        # Add facet relations
        for node in record.findall('overordnetterm-id') + record.findall('ox-id'):
            if node.text not in ids:
                logger.warn('Parent %s not a Concpet or Collection', node.text)
            else:
                broader = resources[ids[node.text]]
                if isinstance(broader, Collection):
                    resource.add('memberOf', broader['id'])
                    broader.add('member', resource['id'])
                if isinstance(broader, Concept) and isinstance(resource, Collection):
                    resource.add('superOrdinate', broader['id'])

        return resource

        # if isinstance(resource, Concept):
        #     parents_transitive = self.get_parents_transitive(parents, tid, [])
        #     if 'HUME06256' in parents_transitive:
        #         logging.info('Setting Geographic')
        #         resource.set_type('Geographic')
            # if 'HUME10852' in parents_transitive:
            #     logging.info('Setting Time')
            #     resource.set_type('Temporal')

    def process_second_level_relations(self, record, resources, ids, terms, uf_terms):

        tid = record.find('term-id').text

        if record.find('se-id') is not None:
            return

        resource = resources[ids[tid]]

        if record.find('gen-se-henvisning') is not None:
            plus_uf_terms = record.find('gen-se-henvisning').text
            for term in plus_uf_terms.split(' * '):
                related = None
                if term.endswith(' (Form)'):
                    term = term[:-7]
                if term in terms:
                    related = resources[terms[term]]
                elif term in uf_terms:
                    related = resources[uf_terms[term]]
                else:
                    logger.warn('Cannot convert relation <%s %s> +USE <%s> because <%s> latter is not a preferred or alternative term of any concept',
                                tid, resource.get('prefLabel.nb').value, plus_uf_terms, term)
                if related is not None:
                    if isinstance(related, Collection):
                        logger.warn(u'Cannot convert relation <%s> USE <%s %s> because the latter is a collection',
                                    tid, resource.get('prefLabel.nb').value, related.id, term)
                    else:
                        resource.add('plusUseTerm', related['id'])

        return resource

    def get_parents_transitive(self, parents, tid, path):
        p = []
        if tid in path:
            logger.warn(u'Uh oh, trapped in a circle: %s', u' → '.join(path + [tid]))
            return p
        for parent in parents.get(tid, []):
            p.append(parent)
            p.extend(self.get_parents_transitive(parents, parent, path + [tid]))
        return p

