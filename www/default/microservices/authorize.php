<?php

function error($msg, $code = '400', $extras = []) {
    header($_SERVER["SERVER_PROTOCOL"]." $code Bad Request"); 
    header('Content-Type: application/json');
    $extras['error'] = $msg;
    echo json_encode($extras);
    exit;
}

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
        error("Not a supported tag");
    }
    $concept_type = $concept_types[$tag];
}

$url = "http://data.ub.uio.no/skosmos/rest/v1/{$vocab}/lookup?" . http_build_query([
    'lang' => 'nb',
    'label' => $_GET['term'],
]);
$res = json_decode(@file_get_contents($url), true);


function out($result) {
    $v = $result['vocab'];
    $n = str_replace('c', '', $result['localname']);

    if ($v == 'realfagstermer') {
        $id = "REAL{$n}";
    } elseif ($v == 'humord') {
        $id = "HUME{$n}";
    } elseif ($v == 'mrtermer') {
        $id = "SMR{$n}";
    } elseif ($v == 'lskjema') {
        $id = "UJUR{$n}";
    } else {
        error('Unknown vocabulary');
    }

    $prefix = '(NO-TrBIB)';
    $out = [
        'id' => $prefix . $id,
        'prefLabel' => $result['prefLabel'],
        // 'data' => $result,
    ];
    header('Content-Type: application/json');
    echo json_encode($out);
    exit;
}

header('Content-Type: text/plain; charset=utf-8');

if (is_null($res)) {
    header($_SERVER["SERVER_PROTOCOL"]." 404 Not Found"); 
    exit;
}

$matching = [];
foreach ($res['result'] as $res) {
    if (is_null($concept_type)) {
        $matching[] = $res;
    } elseif (in_array($concept_type, $res['type'])) {
        $matching[] = $res;
    }
}
if (count($matching) == 0) {
    error('Not found', '404');
} else if (count($matching) > 1) {
    error('Term matched more than one concept');
}
out($matching[0]);

