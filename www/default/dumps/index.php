<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="x-ua-compatible" content="ie=edge, chrome=1" />
<title>Dumps - data.ub.uio.no</title>
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" integrity="sha384-1q8mTJOASx8j1Au+a5WDVnPi2lkFfwwEAa8hDDdjZlpLegxhjVME1fgjWPGmkzs7" crossorigin="anonymous">
  <link rel="stylesheet" href="/site.css" />
  <link href='https://fonts.googleapis.com/css?family=Inconsolata:400,700' rel='stylesheet' type='text/css'>
</head>
<body>

<div class="pagecontainer">

<h1><a href="/">data.ub.uio.no</a> / dumps</h1>

<p>
  All data available under the <a href="http://creativecommons.org/publicdomain/zero/1.0/">Creative Commons CC0 license</a>.
</p>

<?php

$datasets = array(
    'humord' => array(
        'title' => 'HUME: Humord',
        'git' => 'https://github.com/scriptotek/humord',
        'freq' => 'weekly',
    ),
    'realfagstermer' => array(
        'title' => 'REAL: Realfagstermer',
        'git' => 'https://github.com/realfagstermer/realfagstermer',
        'skosmos' => 'https://skosmos.biblionaut.net/realfagstermer/',
        'freq' => 'hourly on changes',
    ),
    'mrtermer' => array(
        'title' => 'SMR: Menneskerettighetstermer',
        'git' => 'https://github.com/realfagstermer/mrtermer',
        'freq' => 'now and then',
    ),
    'lskjema' => array(
        'title' => 'UJUR: L-skjema (Juridiske emneord)',
        'freq' => 'irregularly',
    ),
    'usvd' => array(
        'title' => 'USVD: The UBO relative index to DDC',
        'git' => 'https://github.com/scriptotek/usvd',
        'freq' => 'irregularly',
    ),
);

function fsize_hr($f) {
    $fsize =  filesize($f);
    return ($fsize > 1024*1024) ? round($fsize/1024/124)/10 . ' MB' : round($fsize/1024) . ' kB';
}

function dataset_file($f, $files) {
    if (!in_array($f, $files)) {
        return '<em>not available</em>';
    } else {
        return '<a href="' . $f . '">uncompressed</a> (' . fsize_hr($f) . ')'
            . ' · <a href="' . $f . '.bz2">bz2</a> (' . fsize_hr($f . '.bz2') . ')'
            . ' · <a href="' . $f . '.zip">zip</a> (' . fsize_hr($f . '.zip') . ')'
            ;
    }
}

foreach ($datasets as $dataset => $details) {
    echo '<h2><a class="anchor" name="' . $dataset . '">'. $details['title'] . '</a></h2>';
    $files = glob($dataset . '*');
    echo '<p>';
    // echo 'Updated ' . $details['freq'] . '. ';
    if (count($files)) {
        echo 'Last updated: ' . date ("Y-m-d H:i:s", filemtime($files[0])) . '. ';
    }
    if (isset($details['git'])) {
        echo '<a href="' . $details['git'] . '">Git repo</a>';
    }
    echo '</p>';
    echo '<ul>';

    echo '  <li>Core vocabulary + mappings as MARC21: ' . dataset_file($dataset .'.marc21.xml', $files) . '</li>';
    echo '  <li>Core vocabulary (without mappings) as RDF/Turtle: ' . dataset_file($dataset .'.ttl', $files) . '</li>';
    echo '  <li>Core vocabulary + mappings as RDF/Turtle: ' . dataset_file($dataset .'.complete.ttl', $files) . '</li>';
    echo '  <li>Mappings only as RDF/Turtle: ' . dataset_file($dataset .'.mappings.ttl', $files) . '</li>';

    // foreach ($files as $f) {
    //     echo '<li><a href="' . $f . '">' . $f . '</a> (' . $fsize . ')</li>';
    // }
    echo '</ul>';
}

?>
</div>



</body>
</html>

