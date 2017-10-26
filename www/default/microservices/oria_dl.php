<?php

$schema = <<<EOT

<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
label {
    display:block;
}
input[@type="text"] {
    width: 500px;
}
</style>
</head>
<body>
    <form method="GET" action="oria_dl.php">
      <label>
        template:
        <input type="text" name="template" value="lsr05,contains,urealsamling42&lsr20,contains,{input}">
      </label>
      <label>
        input:
        <input type="text" name="input" value="Gravitasjon">
      </label>
      <button type="submit" name="go">Søk</button>
      <button type="submit" name="getUrl">Bare gi meg URL-en</button>
    </form>
</body>
</html>
EOT;

if (!isset($_GET['input']) || !isset($_GET['template'])) {
    echo $schema; 
    die;
}

$query_input = $_GET['input'];
$query_template = $_GET['template'];
$query_template = str_replace('{input}', $query_input, $query_template);

$qs = [
    'institution' => 'UBO',
    'vid' => 'UBO',
    'search_scope' => 'default_scope',
];

$url = 'https://bibsys-almaprimo.hosted.exlibrisgroup.com/primo_library/libweb/action/dlSearch.do?' . http_build_query($qs) ;

foreach(explode('&', $query_template) as $q) {
    $url .= '&query=' . urlencode($q);
}

if (isset($_GET['go'])) {
    header('Location: ' . $url);
    exit;
}

echo $url;

