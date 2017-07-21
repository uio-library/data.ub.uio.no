<?php

$inp = $_GET['number'];
$inp = preg_replace('/[^0-9.]/', '', $inp);

$res = json_decode(file_get_contents("http://data.ub.uio.no/sparql?query=PREFIX%20skos%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F2004%2F02%2Fskos%2Fcore%23%3E%0A%0ASELECT%20%3Flabel%20%0AWHERE%20%7B%0A%20%20%3Fc%20skos%3AprefLabel%20%3Flabel%20.%0A%20%20%3Fc%20skos%3AinScheme%20%3Chttp%3A%2F%2Fdewey.info%2Fscheme%2Fedition%2Fe23%2F%3E%20.%0A%20%20%3Fc%20skos%3Anotation%20%22{$inp}%22%0A%7D&format=json"), true);


header('Content-Type: text/plain; charset=utf-8');

if (!isset($res['results']['bindings'][0]['label'])) {
    header($_SERVER["SERVER_PROTOCOL"]." 404 Not Found"); 
    exit;
}
echo $res['results']['bindings'][0]['label']['value'];

