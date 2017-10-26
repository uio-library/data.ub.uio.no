<?php

require('vendor/autoload.php');

use Scriptotek\Sru\Client as SruClient;
use Scriptotek\Sru\Exceptions\SruErrorException;
use Scriptotek\Marc\Record;

function error($msg, $extras = []) {
    header($_SERVER["SERVER_PROTOCOL"]." 400 Bad Request"); 
    header('Content-Type: application/json');
    $extras['error'] = $msg;
    echo json_encode($extras);
    exit;
}

// Parse input
$tag_map = [
    '600' => '100',
    '610' => '110',
    '61l' => '111',
    '630' => '130',
];

function query_from_input($input) {
    global $tag_map;
    if (isset($input['tag'])) {
        if (!isset($tag_map[$input['tag']])) {
            error('Not a supported tag. Supported tags are: ' . implode(', ', array_keys($tag_map)));
        }
        $tag = $tag_map[$input['tag']];
    } else {
        $tag = null;
    }
    if (!isset($input['term'])) {
        error('No "term" given');
    }
    $value = $input['term'];
    return [$tag, $value];
}

list($tag, $value) = query_from_input($_GET);
//list($tag, $value) = query_from_input([
//    'tag' => '600',
//    'term' => 'Habsburg slekten',
//]);

if (is_null($tag)) {
    $query = "cql.allIndexes=\"{$value}\"";
} else {
    $query = "marc.{$tag}=\"{$value}\"";
}

$url = 'https://authority.bibsys.no/authority/rest/sru';
$schema = 'marcxchange';
$sru_version = '1.1';

$sru = new SruClient($url, [
    'schema' => $schema,
    'version' => $sru_version,
    'headers' => [],
]);

try {
    $records = iterator_to_array($sru->all($query));
} catch(SruErrorException $e) {
    // var_dump($e);
    error($e->getMessage(), ['uri' => $e->uri]);
}

function format_record($record) {
    global $tag_map;
    $record = Record::fromString((string) $record);
    $out = [];
    $prefix = '(' . $record->query('003')->text() . ')';
    $out['id'] = $prefix . $record->query('001')->text();
    foreach (array_values($tag_map) as $tag) {
        $field = $record->query((string) $tag)->first();
        if (is_null($field)) {
            continue;
        }
        $term = [];
        $val = [];
        foreach ($field->getSubfields() as $sf) {
            $val[] = '$' . $sf->getCode() . ' ' . $sf->getData();
            $term[] = $sf->getData();
        }
        $out['tag'] = $tag;
        $out['vocab'] = 'bare';
        $out['prefLabel'] = implode(' : ', $term);
        $out['field'] = implode(' ', $val);
    }
    return $out;
}

$recs = [];
foreach ($records as $r) {
    $rec = format_record($r);
    if ($rec['prefLabel'] == $value) {
        $recs[] = $rec;
    }
}

header('Content-Type: application/json');
echo json_encode([
    'result' => $recs,
]);

