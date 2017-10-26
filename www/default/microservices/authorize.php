<?php

function error($msg, $code = '400', $extras = []) {
    header($_SERVER["SERVER_PROTOCOL"]." $code Bad Request"); 
    header('Content-Type: application/json');
    $extras['error'] = $msg;
    echo json_encode($extras);
    exit;
}

$concept_types = [
    '648' => ['http://data.ub.uio.no/onto#Time'],
    '650' => ['http://data.ub.uio.no/onto#Topic', 'http://data.ub.uio.no/onto#CompoundConcept'],
    '651' => ['http://data.ub.uio.no/onto#Place'],
    '655' => ['http://data.ub.uio.no/onto#GenreForm'],
    '600' => ['http://data.ub.uio.no/onto#Person'],
    '610' => ['http://data.ub.uio.no/onto#Corporation'],
    '611' => ['http://data.ub.uio.no/onto#Meeting'],
];



$vocab = $_GET['vocabulary'];

$tag = isset($_GET['tag']) ? $_GET['tag'] : null;
$concept_type = null;
if (!is_null($tag)) {
    if (!isset($concept_types[$tag])) {
        error("Not a supported tag");
    }
    $concept_type = $concept_types[$tag];
}

if ($vocab == 'bare') {
    $concept_type = null;
}

if ($vocab == 'bare') {
    $url = "http://data.ub.uio.no/microservices/bare.php?" . http_build_query([
        'tag' => $tag,
        'term' => $_GET['term'],
    ]);
    $res = json_decode(@file_get_contents($url), true);

} else {
    $url = "http://data.ub.uio.no/skosmos/rest/v1/{$vocab}/lookup?" . http_build_query([
        'lang' => 'nb',
        'label' => $_GET['term'],
    ]);
    $res = json_decode(@file_get_contents($url), true);
}
function out($result) {
    $v = $result['vocab'];

    if (isset($result['localname'])) {
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
    } else {
        $id = str_replace('(NO-TrBIB)', '', $result['id']);
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
    error('Not found', '404');
}

$matching = [];
foreach ($res['result'] as $res) {
    if (is_null($concept_type)) {
        $matching[] = $res;
    } else {
        foreach ($res['type'] as $t) {
            if (in_array($t, $concept_type)) {
                $matching[] = $res;
            }
        }
    }
}
if (count($matching) == 0) {
    error('Not found', '404');
} else if (count($matching) > 1) {
    error('Term matched more than one concept');
}
out($matching[0]);

