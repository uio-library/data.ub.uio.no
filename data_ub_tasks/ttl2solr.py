# encoding=utf8

from rdflib.graph import Graph, Literal
from rdflib.namespace import Namespace, URIRef, OWL, RDF, DC, DCTERMS, FOAF, XSD, SKOS, RDFS
import json
import argparse
import logging
import logging.handlers
from six import text_type
from copy import copy

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s %(levelname)s] %(message)s')

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

WD = Namespace('http://data.ub.uio.no/webdewey-terms#')
MARC21 = Namespace('http://data.ub.uio.no/marc21-terms#')

schema = {
    SKOS.prefLabel: 'prefLabel',
    SKOS.altLabel: 'altLabel',
    SKOS.definition: 'definition',
    SKOS.scopeNote: 'scopeNote',
    SKOS.notation: 'notation',
    WD.including: 'including',
    WD.classHere: 'classHere',
    WD.variantName: 'variantName',
    WD.formerName: 'formerName',
    SKOS.editorialNote: 'editorialNote',
    MARC21.synthesized: 'synthesized',
    RDF.type: 'type',
    OWL.deprecated: 'deprecated',

    # Ignore:
    SKOS.inScheme: None,
    SKOS.topConceptOf: None,
    SKOS.broader: None,
    SKOS.narrower: None,
    SKOS.related: None,
    SKOS.exactMatch: None,
    SKOS.closeMatch: None,
    SKOS.broadMatch: None,
    SKOS.narrowMatch: None,
    SKOS.relatedMatch: None,
    SKOS.historyNote: None,
    OWL.sameAs: None,
    DCTERMS.identifier: None,
    DCTERMS.modified: None,
    DCTERMS.created: None,
    MARC21.components: None
}

vocabs = {
    URIRef('http://dewey.info/scheme/edition/e23/'): 'ddc23no',
    URIRef('http://data.ub.uio.no/humord'): 'humord'
}


def get_breadcrumbs(paths, parents):
    # print('[{}] Paths: {}'.format(level, len(paths)))

    new_parents_found = False
    out = []

    for path in paths:
        last = path[-1]
        new_parents = parents.get(last, [])
        if len(new_parents) == 0:
            out.append(path)
            continue

        new_parents_found = True
        for parent in new_parents:
            new_path = copy(path)
            new_path.append(parent)
            out.append(new_path)

    paths = out
    # print('  -> {}'.format(len(paths)))
    # print(paths)

    if new_parents_found:
        return get_breadcrumbs(paths, parents)
    else:
        return paths


def ttl2solr(infile, outfile, vocab_name=None):
    logger.info('ttl2solr: Loading %s', infile)
    g = Graph()
    g.parse(infile, format='turtle')

    # Build parent lookup hash
    # logger.debug('Building parent lookup hash')
    parents = {}
    for c, p in g.subject_objects(SKOS.broader):
        c = text_type(c)  # to string
        p = text_type(p)  # to string
        if c not in parents:
            parents[c] = set()
        parents[c].add(p)

    # Build labels lookup hash using two fast passes
    # logger.debug('Building labels lookup hash')
    labels = {}
    for c, p in g.subject_objects(SKOS.altLabel):
        labels[text_type(c)] = text_type(p)
    for c, p in g.subject_objects(SKOS.prefLabel):
        labels[text_type(c)] = text_type(p)  # overwrite altLabel with prefLabel if found

    # logger.debug('Building documents')
    docs = []
    unknown_preds = set()
    for uriref in g.subjects(RDF.type, SKOS.Concept):
        doc = {'id': text_type(uriref)}
        if vocab_name is not None:
            doc['vocabulary'] = vocab_name

        for pred, obj in g.predicate_objects(uriref):
            if pred not in schema:
                if pred not in unknown_preds:
                    logger.warning('Encountered unknown predicate with no mapping to JSON: %s', pred)
                    unknown_preds.add(pred)
                continue
            if pred == SKOS.inScheme and schema[pred] in vocabs:
                doc['vocab'] = vocabs[schema[pred]]
                continue
            if schema[pred] is None:
                continue
            if schema[pred] not in doc:
                doc[schema[pred]] = []

            doc[schema[pred]].append(text_type(obj))

        # Add labels from broader concepts

        bcs = []
        for bc in get_breadcrumbs([[text_type(uriref)]], parents):
            bc = [labels.get(x) for x in reversed(bc[1:])]
            bcs.append('/'.join([x for x in bc if x is not None]))
        doc['paths'] = bcs

        byLevel = [[text_type(uriref)]]  # Level 0
        level = 0
        while True:
            byLevel.append([])
            for x in byLevel[level]:
                byLevel[level + 1].extend(parents.get(x, set()))
            if len(byLevel[level + 1]) == 0:
                break
            level += 1

        for level, items in enumerate(byLevel[1:4]):
            # logger.debug(level, items)
            doc['parentsLevel{}'.format(level + 1)] = [labels[x] for x in items if x in labels]  # Vi mangler labels for enkelt toppetiketter, som f.eks. 'http://data.ub.uio.no/ddc/19'

        docs.append(doc)
    logger.info('ttl2solr: Storing %d documents in %s', len(docs), outfile)
    json.dump(docs, open(outfile, 'w'), indent=2)


def main():

    parser = argparse.ArgumentParser(description='Convert Turtle to SOLR JSON')

    parser.add_argument('infile', nargs=1, help='Input Turtle file')
    parser.add_argument('outfile', nargs=1, help='Output SOLR JSON')
    parser.add_argument('vocabulary', nargs='?', help='Vocabulary name (optional)')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='More verbose output')

    args = parser.parse_args()

    if args.verbose:
        console_handler.setLevel(logging.DEBUG)
    else:
        console_handler.setLevel(logging.INFO)

    in_file = args.infile[0]
    out_file = args.outfile[0]

    ttl2solr(in_file, out_file, args.vocabulary)


if __name__ == '__main__':
    main()
