# encoding=utf-8
import isodate

from rdflib.graph import Graph, Literal
from rdflib.namespace import Namespace, URIRef, OWL, RDF, DC, DCTERMS, FOAF, XSD, SKOS, RDFS
from rdflib.collection import Collection
from rdflib.plugins.serializers.nt import NTSerializer
from otsrdflib import OrderedTurtleSerializer
from six import binary_type
from datetime import datetime
import logging

from .adapter import Adapter
from ..models.resources import Concept
from ..models.resources import Label

import skosify

try:
    from io import BytesIO
    assert BytesIO
except ImportError:
    try:
        from cStringIO import StringIO as BytesIO
        assert BytesIO
    except ImportError:
        from StringIO import StringIO as BytesIO
        assert BytesIO

logger = logging.getLogger(__name__)

ISOTHES = Namespace('http://purl.org/iso25964/skos-thes#')
MADS = Namespace('http://www.loc.gov/mads/rdf/v1#')
SD = Namespace('http://www.w3.org/ns/sparql-service-description#')
LOCAL = Namespace('http://data.ub.uio.no/onto#') # må være data.ub.uio.no/onto# - ellers blir det "humord:onto#Topic" (????)
UOC = Namespace('http://trans.biblionaut.net/class#')


class Skos(Adapter):
    """
    Class for exporting data as SKOS
    """

    typemap = {
        'Group': [SKOS.Collection, ISOTHES.ConceptGroup],
        'Collection': [SKOS.Collection, ISOTHES.ThesaurusArray],
        'Topic': [SKOS.Concept, LOCAL.Topic],
        'Geographic': [SKOS.Concept, LOCAL.Geographic],
        'GenreForm': [SKOS.Concept, LOCAL.GenreForm],
        'Temporal': [SKOS.Concept, LOCAL.Temporal],
        'SplitNonPreferredTerm': [SKOS.Concept, LOCAL.SplitNonPreferredTerm],
        'CompoundHeading': [SKOS.Concept, LOCAL.ComplexConcept],
        'VirtualCompoundHeading': [SKOS.Concept, LOCAL.VirtualComplexConcept],
        'LinkingTerm': [SKOS.Concept, LOCAL.LinkingTerm],
        'Class': [SKOS.Concept, LOCAL.Class],
    }

    options = {
        'include_narrower': False
    }

    def __init__(self, vocabulary, include=None, mappings_from=None, add_same_as=None,
                 with_ccmapper_candidates=False, infer=False, infer_top_concepts=False):
        """
            - vocabulary : Vocabulary object
            - include : List of files to include
            - mappings_from : List of files to only include mapping relations from
        """
        super(Skos, self).__init__()
        self.vocabulary = vocabulary
        if include is None:
            self.include = []
        else:
            self.include = include
        if mappings_from is None:
            self.mappings_from = []
        else:
            self.mappings_from = mappings_from
        if add_same_as is None:
            self.add_same_as = []
        else:
            self.add_same_as = add_same_as
        self.with_ccmapper_candidates = with_ccmapper_candidates
        self.infer = infer
        self.infer_top_concepts = infer_top_concepts

    @staticmethod
    def get_label(graph: Graph, predicate, lang):
        for tr in graph.triples((predicate, SKOS.prefLabel, None)):
            if tr[2].language == lang:
                return tr[2].value

    def load(self, filename):
        """
        Note: This loader only loads categories and mappings
        """
        graph = Graph()
        graph.parse(filename, format=self.extFromFilename(filename))

        logger.info('Read %d triples from %s', len(graph), filename)

        skosify.infer.skos_symmetric_mappings(graph, related=False)
        #logger.info(f'load({filename})')
        # Load mappings
        n_mappings = 0
        n_memberships = 0
        for tr in graph.triples_choices((None, [SKOS.exactMatch, SKOS.closeMatch, SKOS.broadMatch, SKOS.narrowMatch, SKOS.relatedMatch], None)):
            source_concept = tr[0]
            res_id = self.vocabulary.id_from_uri(source_concept)
            if res_id is not None:
                shortName = str(tr[1]).split('#')[1]
                try:
                    self.vocabulary.resources[res_id].add('mappings.%s' % shortName, str(tr[2]))
                    n_mappings += 1
                except KeyError:
                    pass #logger.warning('Concept not found: %s', res_id)
        # Load categories
        for tr in graph.triples((None, RDF.type, UOC.Category)):
            cat_lab = self.get_label(graph, tr[0], 'nb')
            if cat_lab is None:
                raise Exception(f'Category not found: {tr[0]}')
            cat_id = '' + tr[0]

            cat = Concept().set_type('Category')
            cat.set('id', cat_id)
            cat.set('prefLabel.nb', Label(cat_lab))
            self.vocabulary.resources.load([cat])

            for tr2 in graph.triples((tr[0], SKOS.member, None)):
                uri = str(tr2[2])
                res_id = self.vocabulary.id_from_uri(uri)
                if res_id is not None:
                    try:
                        self.vocabulary.resources[res_id].add('memberOf', cat_id)
                        n_memberships += 1
                    except KeyError:
                        pass #logger.warning('KeyError: Concept not found: %s', res_id)
        logger.info('Begin CCMapper')
        # Load number of ccmapper mapping candidates
        for tr in graph.triples((None, LOCAL.ccmapperCandidates, None)):
            #logger.info(tr)
            source_concept = tr[0]
            res_id = self.vocabulary.id_from_uri(source_concept)
            if res_id is not None:
                shortName = str(tr[1]).split('#')[1]
                try:
                    self.vocabulary.resources[res_id].set('ccmapperCandidates', int(tr[2]))
                except KeyError:
                    pass # just ignore it i guess 1
                    #logger.warning('CCMapper candidate // Concept not found: %s', res_id)

        # Load ccmapper mapping state
        for tr in graph.triples((None, LOCAL.ccmapperState, None)):
            source_concept = tr[0]
            res_id = self.vocabulary.id_from_uri(source_concept)
            if res_id is not None:
                shortName = str(tr[1]).split('#')[1]
                try:
                    self.vocabulary.resources[res_id].set('ccmapperState', tr[2])
                except KeyError:
                    pass # just ignore it i guess 2
                    #logger.warning('CCMapper state // Concept not found: %s', res_id)

        logger.info('Loaded %d mappings and %d category memberships from %s', n_mappings, n_memberships, filename)

    def prepare(self):
        logger.info('Building RDF graph')

        graph = Graph()

        for inc in self.include:
            lg0 = len(graph)
            graph.parse(inc, format=self.extFromFilename(inc))
            logger.info(' - Included {} triples from {}'.format(len(graph) - lg0, inc))

        try:
            scheme_uri = next(graph.triples((None, RDF.type, SKOS.ConceptScheme)))
        except StopIteration:
            raise Exception('Concept scheme URI could not be found in vocabulary scheme data')
        scheme_uri = scheme_uri[0]

        now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        graph.set((URIRef(scheme_uri), DCTERMS.modified, Literal(now, datatype=XSD.dateTime)))

        lg0 = len(graph)
        for resource in self.vocabulary.resources:
            self.convert_resource(graph, resource, self.vocabulary.resources, scheme_uri,
                                  self.vocabulary.default_language.alpha2)
        logger.info(' - Added {} triples'.format(len(graph) - lg0))

        all_concepts = set([tr[0] for tr in graph.triples((None, RDF.type, SKOS.Concept))])
        for inc in self.mappings_from:
            lg0 = len(graph)
            mappings = self.load_mappings(inc)
            for tr in mappings.triples((None, None, None)):
                if tr[0] in all_concepts:
                    graph.add(tr)
            logger.info(' - Added {} mappings from {}'.format(len(graph) - lg0, inc))

        logger.info('Skosify...')
        self.skosify_process(graph)
        return {'graph': graph}

    def serialize(self, graph, format='turtle'):
        logger.info('Serializing RDF graph as %s' % format)

        if format == 'nt':
            serializer = NTSerializer(graph)

        elif format == 'turtle':
            serializer = OrderedTurtleSerializer(graph)

            # These will appear first in the file and be ordered by URI
            serializer.class_order = [SKOS.ConceptScheme,
                                     FOAF.Organization,
                                     SD.Service,
                                     SD.Dataset,
                                     SD.Graph,
                                     SD.NamedGraph,
                                     OWL.Ontology,
                                     OWL.Class,
                                     OWL.DatatypeProperty,
                                     SKOS.Collection,
                                     SKOS.Concept]

            serializer.sorters_by_class = {
                SKOS.Concept: [
                    ('.*?/[^0-9]*([0-9.]+)$', lambda x: float(x[0])),
                ]
            }
        else:
            raise ValueError('Unknown format %s' % format)

        stream = BytesIO()
        serializer.serialize(stream)
        return stream.getvalue()

    def convert_types(self, types):
        out = []
        for x in types:
            for y in self.typemap.get(x, []):
                out.append(y)
        return out

    def try_resolve_relations(self, resources, resource, key):
        out = []
        for value in resource.get(key, []):
            try:
                other_resource = resources.get(id=value)
                out.append(URIRef(self.vocabulary.uri(other_resource.id)))
            except KeyError:
                raise Exception('Posten %s referer til en ugyldig ID: %s' % (resource['id'], value))
        return out

    def convert_resource(self, graph, resource, resources, scheme_uri, default_language):
        uri = URIRef(self.vocabulary.uri(resource['id']))
        # funka ikke, sier dette ikke er en rdfterm uri = uri.replace("http:","https:")
        types = self.convert_types(resource.get('type', []))
        if len(types) == 0:
            # Unknown type, log it?
            #logger.warn("UNKNOWN TYPE/S")
            return
        for value in types:
            graph.add((uri, RDF.type, value))

        if resource.get('isTopConcept'):
            #logger.info(resource.get('isTopConcept'))
            graph.add((uri, SKOS.topConceptOf, scheme_uri))
        else:
            graph.add((uri, SKOS.inScheme, scheme_uri))

        for lang, term in resource.get('prefLabel', {}).items():
            graph.add((uri, SKOS.prefLabel, Literal(term.value, lang=lang)))

            if term.hasAcronym:
                # @TODO Temporary while thinking...
                # graph.add((uri, LOCAL.acronym, Literal(term['hasAcronym'], lang=lang)))
                graph.add((uri, SKOS.altLabel, Literal(term.hasAcronym, lang=lang)))

        for lang, terms in resource.get('altLabel', {}).items():
            for term in terms:
                graph.add((uri, SKOS.altLabel, Literal(term.value, lang=lang)))

                if term.hasAcronym:
                    # @TODO Temporary while thinking...
                    # graph.add((uri, LOCAL.acronym, Literal(term['hasAcronym'], lang=lang)))
                    graph.add((uri, SKOS.altLabel, Literal(term.hasAcronym, lang=lang)))

        for lang, value in resource.get('definition', {}).items():
            graph.add((uri, SKOS.definition, Literal(value, lang=lang)))

        for lang, values in resource.get('scopeNote', {}).items():
            for value in values:
                graph.add((uri, SKOS.scopeNote, Literal(value, lang=lang)))

        for value in resource.get('editorialNote', []):
            graph.add((uri, SKOS.editorialNote, Literal(value, lang=default_language)))

        for value in resource.get('acronym', []):
            graph.add((uri, LOCAL.acronym, Literal(value)))

        for value in resource.get('notation', []):
            graph.add((uri, SKOS.notation, Literal(value)))

        x = resource.get('created')
        if x is not None:
            graph.add((uri, DCTERMS.created, Literal(x, datatype=XSD.dateTime)))

        x = resource.get('deprecated')
        if x is not None:
            graph.add((uri, OWL.deprecated, Literal(True)))
            graph.add((uri, SKOS.historyNote, Literal('Deprecated on {}'.format(x), lang='en')))
            graph.add((uri, DCTERMS.modified, Literal(x, datatype=XSD.dateTime)))
        else:
            x = resource.get('modified', resource.get('created'))
            if x is not None:
                graph.add((uri, DCTERMS.modified, Literal(x, datatype=XSD.dateTime)))

        x = resource.get('elementSymbol')
        if x is not None:
            graph.add((uri, LOCAL.elementSymbol, Literal(x)))

        if self.with_ccmapper_candidates:
            x = resource.get('ccmapperCandidates')
            if x is not None:
                #logger.info('CCMapperCandidates is not None:',x)
                graph.add((uri, LOCAL.ccmapperCandidates, Literal(x, datatype=XSD.integer)))
            x = resource.get('ccmapperState')
            if x is not None:
                #logger.info('CCMapperState is not None:',x)
                graph.add((uri, LOCAL.ccmapperState, Literal(x)))

        for x in resource.get('libCode', []):
            graph.add((uri, LOCAL.libCode, Literal(x)))

        x = resource.get('id')
        if x is not None:
            graph.add((uri, DCTERMS.identifier, Literal(x)))

        for x in resource.get('ddc', []):
            graph.add((uri, DCTERMS.DDC, Literal(x)))

        for x in resource.get('msc', []):
            graph.add((uri, LOCAL.MSC, Literal(x)))

        for other_uri in self.try_resolve_relations(resources, resource, 'related'):
            if 'Collection' in resource.get('type', []):
              #  logger.warn(u'Skipping <%s> skos:related <%s> because the former is a collection',
              #              uri, other_uri)
              pass
            else:
                graph.add((uri, SKOS.related, other_uri))

        for other_uri in self.try_resolve_relations(resources, resource, 'plusUseTerm'):
            graph.add((uri, LOCAL.plusUseTerm, other_uri))

        for other_uri in self.try_resolve_relations(resources, resource, 'replacedBy'):
            graph.add((uri, DCTERMS.isReplacedBy, other_uri))

        for other_uri in self.try_resolve_relations(resources, resource, 'member'):
            graph.add((uri, SKOS.member, other_uri))

        for other_uri in self.try_resolve_relations(resources, resource, 'memberOf'):
            graph.add((other_uri, SKOS.member, uri))

        for other_uri in self.try_resolve_relations(resources, resource, 'superOrdinate'):
            graph.add((uri, ISOTHES.superOrdinate, other_uri))
            graph.add((other_uri, ISOTHES.subordinateArray, uri))

        for other_uri in self.try_resolve_relations(resources, resource, 'broader'):
            graph.add((uri, SKOS.broader, other_uri))
            if self.options['include_narrower']:
                graph.add((other_uri, SKOS.narrower, uri))

        for mapping_type, target_uris in resource.get('mappings', {}).items():
            for target_uri in target_uris:
                graph.add((uri, SKOS[mapping_type], URIRef(target_uri)))

        components = [resources.get(id=value) for value in resource.get('component', [])]
        if len(components) != 0:

            # @TODO: Generalize
            fallback_lang = 'nb'
            for lang in ['nb', 'nn', 'en']:
                labels = [component['prefLabel'].get(lang, component['prefLabel'].get(fallback_lang)) for component in components]
                logger.info(labels)
                labels = [component.value for component in labels if component]
                # labels = [c.prefLabel[lang].value for c in components if c['prefLabel'].get(lang, fallback_lang)]
                logger.info(labels)
                #raise KeyboardInterrupt('INTENTIONAL CRASH - DISREGARD')
                if len(labels) == len(components):
                    streng = resources.string_separator.join(labels)
                    graph.add((uri, SKOS.prefLabel, Literal(streng, lang=lang)))
                else:
                    logger.info("label error")

            component_uris = [URIRef(self.vocabulary.uri(c['id'])) for c in components]

            for component_uri in component_uris:
                graph.add((uri, LOCAL.component, component_uri))
                graph.add((uri, SKOS.broader, component_uri))
                if self.options['include_narrower']:
                    graph.add((component_uri, SKOS.narrower, uri))
                    graph.add((component_uri, LOCAL.compound, uri))

        for same_as in self.add_same_as:
            graph.add((uri, OWL.sameAs, URIRef(same_as.format(id=resource['id']))))

    def setup_top_concepts(self, graph):
        for cs in sorted(graph.subjects(RDF.type, SKOS.ConceptScheme)):
            for conc in sorted(graph.subjects(SKOS.inScheme, cs)):
                if (conc, RDF.type, SKOS.Concept) not in graph:
                    continue  # not a Concept, so can't be a top concept
                if (conc, RDF.type, LOCAL.SplitNonPreferredTerm) in graph:
                    continue  # can't be a top concept
                # check whether it's a top concept
                broader = graph.value(conc, SKOS.broader, None, any=True)
                if broader is None:  # yes it is a top concept!
                    if (cs, SKOS.hasTopConcept, conc) not in graph and (conc, SKOS.topConceptOf, cs) not in graph:
               #         logging.info("Marking loose concept %s as top concept of scheme %s", conc, cs)
                        graph.add((cs, SKOS.hasTopConcept, conc))
                        graph.add((conc, SKOS.topConceptOf, cs))
    def skosify_process(self, graph):
        # check hierarchy for problems
        skosify.check.hierarchy_cycles(graph, True)
        skosify.check.disjoint_relations(graph, True)
        skosify.check.hierarchical_redundancy(graph, True)
        # skosify.check.preflabel_uniqueness(graph, 'shortest')
        # skosify.check.label_overlap(graph, True)

        if self.infer_top_concepts:
            self.setup_top_concepts(graph)

        if self.infer:
            rules = [
                # S40
                (SKOS.exactMatch, RDFS.subPropertyOf, SKOS.mappingRelation),
                (SKOS.closeMatch, RDFS.subPropertyOf, SKOS.mappingRelation),
                (SKOS.broadMatch, RDFS.subPropertyOf, SKOS.mappingRelation),
                (SKOS.narrowMatch, RDFS.subPropertyOf, SKOS.mappingRelation),
                (SKOS.relatedMatch, RDFS.subPropertyOf, SKOS.mappingRelation),

                # S42
                # (SKOS.exactMatch, RDFS.subPropertyOf, SKOS.closeMatch),
            ]

            for rule in rules:
                graph.add(rule)

            skosify.infer.rdfs_properties(graph)

            for rule in rules:
                graph.remove(rule)
            skosify.infer.skos_topConcept(graph)
