<?php

$concept_types = [
    '648' => 'http://data.ub.uio.no/onto#Time',
    '650' => 'http://data.ub.uio.no/onto#Topic',
    '651' => 'http://data.ub.uio.no/onto#Place',
    '655' => 'http://data.ub.uio.no/onto#GenreForm',
];


$vocab = $_GET['vocabulary'];

$tag = $_GET['tag'];
$concept_type = null;
if (!is_null($tag)) {
    if (!isset($concept_types[$tag])) {
        header($_SERVER["SERVER_PROTOCOL"]." 400 Bad Request"); 
        echo "Not a supported tag";
        exit;
    }
    $concept_type = $concept_types[$tag];
}

$url = "http://data.ub.uio.no/skosmos/rest/v1/{$vocab}/search?" . http_build_query([
    'lang' => 'nb',
    'query' => $_GET['term'],
]);
$res = json_decode(file_get_contents($url), true);


function out($result) {
    $v = $result['vocab'];
    $n = str_replace('c', '', $result['localname']);

    if ($v == 'realfagstermer') {
        echo "REAL{$n}";
    } elseif ($v == 'humord') {
        echo "HUME{$n}";
    } elseif ($v == 'mrtermer') {
        echo "SMR{$n}";
    } else {
        header($_SERVER["SERVER_PROTOCOL"]." 404 Not Found"); 
    }
    exit;
}

header('Content-Type: text/plain; charset=utf-8');

if (is_null($res)) {
    header($_SERVER["SERVER_PROTOCOL"]." 404 Not Found"); 
    exit;
}

foreach ($res['results'] as $res) {
    if (is_null($concept_type)) {
        out($res);
    } elseif (in_array($concept_type, $res['type'])) {
        out($res);
    }
}

header($_SERVER["SERVER_PROTOCOL"]." 404 Not Found"); 
