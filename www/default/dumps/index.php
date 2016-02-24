<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="x-ua-compatible" content="ie=edge, chrome=1" />
<title>dumps - data.ub.uio.no</title>
<link rel="stylesheet" href="site.css" />
</head>
<body>

<h1><a href="http://data.ub.uio.no/">data.ub.uio.no</a> &gt; dumps</h1>
<p>
  All data is available under the <a href="http://creativecommons.org/publicdomain/zero/1.0/">Creative Commons CC0 license</a>.
</p>
<p>
  Note: There are currently problems with the automatic update system.
</p>
<?php

$datasets = array(
    'realfagstermer' => array(
        'title' => 'Realfagstermer',
        'git' => 'https://github.com/realfagstermer/realfagstermer',
        'skosmos' => 'https://skosmos.biblionaut.net/realfagstermer/',
        'freq' => 'hourly on changes',
    ),
    'humord' => array(
        'title' => 'Humord',
        'git' => 'https://github.com/scriptotek/humord',
        'freq' => 'weekly',
    ),
    'mrtermer' => array(
        'title' => 'Menneskerettighetstermer',
        'git' => 'https://github.com/realfagstermer/mrtermer',
        'freq' => 'now and then',
    ),
    'usvd' => array(
        'title' => 'The UBO relative index to DDC',
        'git' => 'https://github.com/scriptotek/usvd',
        'freq' => 'irregularly',
    ),
);

foreach ($datasets as $dataset => $details) {
    echo '<h2><a class="anchor" name="' . $dataset . '">'. $details['title'] . '</a></h2>';
    $files = glob($dataset . '*');
    echo '<p>';
    echo 'Updated ' . $details['freq'] . '. ';
    echo 'Last update: ' . date ("Y-m-d H:i:s", filemtime($files[0])) . '. ';
    echo '<a href="' . $details['git'] . '">Git repo</a>';
    echo '</p>';
    echo '<ul>';
    foreach ($files as $f) {
        $fsize =  filesize($f);
        $fsize = ($fsize > 1024*1024) ? round($fsize/1024/124)/10 . ' MB' : round($fsize/1024) . ' kB';
        echo '<li><a href="' . $f . '">' . $f . '</a> (' . $fsize . ')</li>';
    }
    echo '</ul>';
}

?>



</body>
</html>

