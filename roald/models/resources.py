# encoding=utf-8
import isodate
import json
import codecs
from copy import deepcopy
from six import text_type
from ..util import array_set, array_add, array_get
from ..errors import InvalidDataException

try:
    from functools import reduce  # Python
except:
    pass

class Label(object):

    def __init__(self, value=None):
        self.value = None
        self.hasAcronym = None
        self.acronymFor = None
        # lang = None

        if value is not None:
            self.value = value

    def set(self, key, value):
        self.__setattr__(key, value)
        return self  # for chaining

    def load(self, data):
        self.value = data.get('value')
        self.hasAcronym = data.get('hasAcronym')
        self.acronymFor = data.get('acronymFor')
        # self.lang = data.get('lang')
        return self  # for chaining

    def serialize(self):
        o = {}
        if self.value:
            o['value'] = self.value
        if self.hasAcronym:
            o['hasAcronym'] = self.hasAcronym
        if self.acronymFor:
            o['acronymFor'] = self.acronymFor
        return o

    def __str__(self):
        return self.value

    def __repr__(self):
        return u'"{}"'.format(self.value)


class Resource(object):

    def __init__(self, uri_formatter=None):
        super(Resource, self).__init__()
        self.blank = True
        self.uri_formatter = uri_formatter
        self._data = {
            'prefLabel': {},
            'altLabel': {},
            'hiddenLabel': {}
        }

    @property
    def prefLabel(self):
        return self._data['prefLabel']

    @prefLabel.setter
    def prefLabel(self, value):
        self._data['prefLabel'] = value

    @property
    def altLabel(self):
        return self._data['altLabel']

    @altLabel.setter
    def altLabel(self, value):
        self._data['altLabel'] = value

    @property
    def hiddenLabel(self):
        return self._data['hiddenLabel']

    @hiddenLabel.setter
    def hiddenLabel(self, value):
        self._data['hiddenLabel'] = value

    def load(self, data):
        self._data = deepcopy(data)
        if 'prefLabel' not in self._data:
            self._data['prefLabel'] = {}
            self._data['altLabel'] = {}
            self._data['hiddenfLabel'] = {}

        for lang, label in self._data.get('prefLabel', {}).items():
            array_set(self._data, 'prefLabel.{}'.format(lang), Label().load(label))

        for lang, labels in self._data.get('altLabel', {}).items():
            array_set(self._data, 'altLabel.{}'.format(lang), [Label().load(label) for label in labels])

        for lang, labels in self._data.get('hiddenLabel', {}).items():
            array_set(self._data, 'hiddenLabel.{}'.format(lang), [Label().load(label) for label in labels])

        return self  # for chaining

    def serialize(self):
        data = deepcopy(self._data)

        for lang, label in data.get('prefLabel', {}).items():
            data['prefLabel'][lang] = data['prefLabel'][lang].serialize()

        for lang, labels in self._data.get('altLabel', {}).items():
            data['altLabel'][lang] = [label.serialize() for label in labels]

        for lang, labels in self._data.get('hiddenLabel', {}).items():
            data['hiddenLabel'][lang] = [label.serialize() for label in labels]

        return data

    def add(self, key, value):
        self.blank = False
        array_add(self._data, key, value)
        return self  # for chaining

    def set(self, key, value):
        self.blank = False
        if key.split('.')[0] in ['prefLabel', 'altLabel', 'hiddenLabel'] and not isinstance(value, Label):
            array_set(self._data, key, Label(value), False)
        else:
            array_set(self._data, key, value, False)
        return self  # for chaining

    def get(self, key, default=None):
        return array_get(self._data, key, default)

    def __getitem__(self, key):
        return self._data[key]

    def __contains__(self, key):
        return key in self._data

    def __getattr__(self, name):
        if name in ['__bases__']:
            return object.__getattr__(name)
        if name in self._data:
            return self._data[name]
        raise AttributeError

    def uri(self):  # TODO: Move into Resource class
        if self.uri_formatter is None:
            raise Exception('No URI formatter has been set.')
        return self.uri_formatter.format(id=id[4:])


class Category(Resource):

    def __init__(self):
        super(Category, self).__init__()
        self._data['type'] = 'Category'


class Group(Resource):

    def __init__(self):
        super(Group, self).__init__()
        self._data['type'] = 'Group'


class Collection(Resource):

    def __init__(self):
        super(Collection, self).__init__()
        self._data['type'] = ['Collection']


class Concept(Resource):
    """docstring for Concept"""

    def __init__(self, conceptType=None):
        super(Concept, self).__init__()
        if conceptType is not None:
            self.set_type(conceptType)

    def set_type(self, conceptType):

        if conceptType not in [
            'Topic',
            'Geographic',
            'Temporal',
            'GenreForm',
            'SplitNonPreferredTerm',
            'CompoundHeading',
            'VirtualCompoundHeading',
            'LinkingTerm',
            'Category'
        ]:
            raise ValueError('Invalid concept type')

        conceptTypes = [conceptType]

        # Genre/form can also be used as topic:
        # if conceptType == 'GenreForm':
        #    conceptTypes.append('Topic')

        self._data['type'] = conceptTypes
        return self  # for chaining


class Resources(object):
    """
    Resources class
    """

    string_separator = ' : '

    def __init__(self, uri_format=None):
        """
            - data: dict
            - uri_format : the URI format string, example: 'http://data.me/{id}'
        """
        super(Resources, self).__init__()
        self._uri_format = uri_format
        self.reset()

    @property
    def uri_format(self):
        return self._uri_format

    @uri_format.setter
    def uri_format(self, value):
        self._uri_format = value

    def get(self, id=None, term=None, lang=None):
        if id is not None:
            return self._resource_from_id[id]
        if term is not None and lang is not None:
            return self._resource_from_id[self._id_from_term[term][lang]]
        if term is not None:
            if term not in self._id_from_term:
                raise KeyError('Term not found')
            ids = set(self._id_from_term[term].values())
            if len(ids) > 1:
                raise KeyError('Term maps to more than one concept. Please specify lang.')
            return self._resource_from_id[ids.pop()]
        return self._resources

    def reset(self):
        self._resources = []  # data container
        self._resource_from_id = {}  # fast lookup hash
        self._id_from_term = {}  # fast lookup hash
        self._term_from_id = {}  # fast lookup hash

    def load(self, data):
        """
            data: dict
        """
        if type(data) is not list:
            raise InvalidDataException()

        for el in data:
            rid = el['id']

            if isinstance(el, Resource):
                instance = el
            else:
                if rid in self._term_from_id:
                    raise InvalidDataException('The ID {} is defined more than once.'.format(rid))
                if 'Collection' in el.get('type', []):
                    instance = Collection().load(el)
                elif 'Group' in el.get('type', []):
                    instance = Group().load(el)
                elif 'Category' in el.get('type', []):
                    instance = Category().load(el)
                else:
                    instance = Concept().load(el)

            self._resources.append(instance)
            self._resource_from_id[rid] = instance

            for lang, label in instance.prefLabel.items():
                array_set(self._id_from_term, text_type('{}.{}').format(label.value, lang), rid)
                array_set(self._term_from_id, text_type('{}.{}').format(rid, lang), label.value)

        for res in self._resources:
            rid = res['id']
            if 'component' in res:
                components = [self.get(id=x) for x in res['component']]
                languages = [set(x.prefLabel.keys()) for x in components]
                # Reduce to languages shared by all components
                languages = reduce(lambda x, y: x.intersection(y), languages)

                for lang in languages:
                    term = self.string_separator.join([x.get('prefLabel.{}'.format(lang)).value for x in components])
                    array_set(self._id_from_term, text_type('{}.{}').format(term, lang), rid)
                    array_set(self._term_from_id, text_type('{}.{}').format(rid, lang), term)

        return self  # make chainable

    def serialize(self):
        return [x.serialize() for x in self._resources]

    def __iter__(self):
        for c in self._resources:
            yield c

    def __len__(self):
        return len(self._resources)

    def __getitem__(self, key):
        return self.get(id=key)


class Concepts(Resources):
    """
    Concepts class
    """

    def __init__(self, data={}):
        """
            - data: dict
        """
        super(Concepts, self).__init__()

    def split_compound_heading(self, term):
        parts = [[x.strip()[0], x.strip()[1:].strip()] for x in value.split('$') if len(x.strip()) > 0]
