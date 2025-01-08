# encoding=utf-8
from __future__ import print_function
import isodate
import xmlwitch
import codecs
import os
import re
import logging
from ..models.resources import Concept
from ..models.resources import Label

logger = logging.getLogger(__name__)


class Roald2(object):
    """
    Class for importing legacy data from Roald 2
    """

    elementSymbols = ['Ag', 'Al', 'Am', 'Ar', 'As', 'At', 'Au', 'B', 'Ba', 'Be', 'Bh', 'Bi', 'Bk', 'Br', 'C', 'Ca', 'Cd', 'Ce', 'Cf', 'Cl', 'Cm', 'Cn', 'Co', 'Cr', 'Cs', 'Cu', 'Db', 'Ds', 'Dy', 'Er', 'Es', 'Eu', 'F', 'Fe', 'Fl', 'Fm', 'Fr', 'Ga', 'Gd', 'Ge', 'H', 'He', 'Hf', 'Hg', 'Ho', 'Hs', 'I', 'In', 'Ir', 'K', 'Kr', 'La', 'Li', 'Lr', 'Lu', 'Lv', 'Md', 'Mg', 'Mn', 'Mo', 'Mt', 'N', 'Na', 'Nb', 'Nd', 'Ne', 'Ni', 'No', 'Np', 'O', 'Os', 'P', 'Pa', 'Pb', 'Pd', 'Pm', 'Po', 'Pr', 'Pt', 'Pu', 'Ra', 'Rb', 'Re', 'Rf', 'Rg', 'Rh', 'Rn', 'Ru', 'S', 'Sb', 'Sc', 'Se', 'Sg', 'Si', 'Sm', 'Sn', 'Sr', 'Ta', 'Tb', 'Tc', 'Te', 'Th', 'Ti', 'Tl', 'Tm', 'U', 'Uuo', 'Uup', 'Uus', 'Uut', 'V', 'W', 'Xe', 'Y', 'Yb', 'Zn', 'Zr']

    def __init__(self, vocabulary):
        super(Roald2, self).__init__()
        self.vocabulary = vocabulary

    def load(self, path='./', language_code=None):

        if language_code is None:
            language_code = self.vocabulary.default_language.alpha2

        files = {
            'idtermer.txt': 'Topic',
            'idformer.txt': 'GenreForm',
            'idtider.txt': 'Temporal',
            'idsteder.txt': 'Geographic',
            'idstrenger.txt': 'CompoundHeading',
        }

        resources = []
        for f, t in files.items():
            resources += self.read_file(path + f, t, language_code)

        if len(resources) == 0:
            raise RuntimeError('Found no resources in {}'.format(path))

        self.vocabulary.resources.load(resources)
        logger.info('Loaded %d concepts from %s', len(resources), path)

    def read_file(self, filename, conceptType, language_code):
        print(filename)
        concepts = []
        if not os.path.isfile(filename):
            return []
        f = codecs.open(filename, 'r', 'utf-8')
        for concept in self.read_concept(f.read(), conceptType, language_code):
            if not concept.blank:
                concepts.append(concept)
        f.close()
        return concepts


    def add_acronyms_and_components(self, concept, acronyms, language_code, components):
        for value in acronyms:
            pvalue = re.sub('-', '', value)
            if value in self.elementSymbols:
                concept.set('elementSymbol', value)
            else:
                prefLabel = concept.get('prefLabel.{}'.format(language_code))
                if prefLabel is None or prefLabel.value != value:
                    concept.add('altLabel.{key}'.format(key=language_code), Label(value))
                # print('Check:', value)
                # acronym_for = []
                # for lang, term in concept.get('prefLabel').items():
                #     words = re.split('[ -]+', term.value)
                #     x = 0
                #     for n in range(len(words)):
                #         # print n, words[n], value[x]
                #         if words[n][0].lower() == pvalue[x].lower():
                #             # print ' <> Found'
                #             x += 1
                #             if x >= len(pvalue):
                #                 print(' : matched prefLabel', term.value)
                #                 acronym_for.append(term)
                #                 break
                # for lang, terms in concept.get('altLabel', {}).items():
                #     for term in terms:
                #         words = re.split('[ -]+', term.value)
                #         x = 0
                #         for n in range(len(words)):
                #             # print n, words[n], value[x]
                #             if words[n][0].lower() == pvalue[x].lower():
                #                 # print ' <> Found'
                #                 x += 1
                #                 if x >= len(pvalue):
                #                     print(' : matched altLabel', term.value)
                #                     acronym_for.append(term)
                #                     break
                # if len(acronym_for) == 0:
                #     prefLabels = [term for lang, term in concept.get('prefLabel').items()]
                #     if len(prefLabels) == 1:
                #         acronym_for.append(prefLabels[0])
                # for term in acronym_for:
                #     term.hasAcronym = value
                # if len(acronym_for) == 0:
                #     concept.add('altLabel.{key}'.format(key=language_code), Label(value).set('acronymFor', '?'))

        for co in ['da', 'db', 'dz', 'dy', 'dx']:
            for c in components[co]:
                concept.add('component', c)

        return concept


    def read_concept(self, data, conceptType, language_code):
        concept = Concept().set_type(conceptType)
        acronyms = []
        components = {'da': [], 'db': [], 'dx': [], 'dy': [], 'dz': []}
        lines = data.split('\n')

        # First pass
        for line in lines:
            line = line.strip().split('= ')
            if len(line) == 1:
                if not concept.blank:
                    yield self.add_acronyms_and_components(concept, acronyms, language_code, components)
                acronyms = []
                components = {'da': [], 'db': [], 'dx': [], 'dy': [], 'dz': []}
                concept = Concept().set_type(conceptType)
            else:
                key, value = line
                if key == 'id':
                    # uri = 'http://data.ub.uio.no/realfagstermer/{}'.format(value)
                    # concept.set('uri', uri)
                    concept.set('id', value)
                elif key == 'te':
                    concept.set('prefLabel.{}'.format(language_code), Label(value))
                elif key == 'bf':
                    concept.add('altLabel.{}'.format(language_code), Label(value))
                elif key in ['en', 'nb', 'nn', 'la']:
                    if key not in concept.get('prefLabel'):
                        concept.set('prefLabel.{key}'.format(key=key), Label(value))
                    elif concept.get('prefLabel.{key}'.format(key=key)).value != value:
                        concept.add('altLabel.{key}'.format(key=key), Label(value))

                elif key == 'ak':
                    acronyms.append(value)

                elif key == 'ms':
                    concept.add('msc', value)
                elif key == 'dw':
                    concept.add('ddc', value)

                elif key == 'fly':
                    # uri = 'http://data.ub.uio.no/realfagstermer/{}'.format(value)
                    concept.add('replacedBy', value)
                elif key == 'so':
                    # uri = 'http://data.ub.uio.no/realfagstermer/{}'.format(value)
                    concept.add('related', value)
                elif key == 'ot':
                    # uri = 'http://data.ub.uio.no/realfagstermer/{}'.format(value)
                    concept.add('broader', value)
                elif key == 'ut':
                    pass
                    # concept.add('narrower', value)
                elif key == 'de':
                    concept.set('definition.{}'.format(language_code), value)
                elif key == 'no':
                    # @TODO: Disse har tradisjonelt havnet i skos:editorialNote,
                    #        men de fleste kan antakelig flyttes til scopeNote
                    concept.add('editorialNote', value)
                elif key == 'tio':
                    concept.set('created', value)
                elif key == 'tie':
                    concept.set('modified', value)
                elif key == 'tis':
                    concept.set('deprecated', value)
                elif key == 'ba':
                    for x in value.split(','):
                        if len(x.strip()) > 0:
                            concept.add('libCode', x.strip())
                elif key == 'st':
                    pass
                    # concept.add('streng', value)
                elif key in ['da', 'db', 'dx', 'dy', 'dz']:
                    # uri = 'http://data.ub.uio.no/realfagstermer/{}'.format(value)
                    components[key].append(value)
                    if key in ['dx', 'dy', 'dz']:
                        concept.set_type('VirtualCompoundHeading')

                else:
                    print('Unknown key: {}'.format(key))

        if not concept.blank:
            yield self.add_acronyms_and_components(concept, acronyms, language_code, components)
