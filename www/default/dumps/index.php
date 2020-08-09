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
  All data available under the <a href="http://creativecommons.org/publicdomain/zero/1.0/">Creative Commons CC0 license</a>,
  except Norwegian WebDewey, which is (probably) only available under
<a href="https://creativecommons.org/licenses/by-nc-nd/3.0/">Creative Commons Attribution-Noncommercial-No Derivative Works 3.0 Unported</a>.
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
        'freq' => 'hourly upon changes',
    ),
    'mrtermer' => array(
        'title' => 'SMR: Menneskerettighetstermer',
        'git' => 'https://github.com/realfagstermer/mrtermer',
        'freq' => 'irregularly',
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
    'msc-ubo' => array(
        'title' => 'MSC-UBO: MSC 1970-based classification scheme used at UiO',
        'git' => 'https://github.com/realfagstermer/msc-ubo',
        'freq' => 'irregularly',
    ),
    'wdno' => array(
        'title' => 'WDNO: Norsk WebDewey (DDC 23)',
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

function dataset_files($files, $pattern) {
    $ret = '';
    foreach ($files as $fname) {
        if (preg_match($pattern, $fname)) {
            $setname = explode('.', $fname)[0];
            $ret .= "<li>$setname: " . dataset_file($fname, $files) . "</li>";
        }
    }
    if (empty($ret)) {
        return '<em>not available</em>';
    }
    return $ret;
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
    echo '  <li>Core vocabulary:<ul>';
    echo '    <li>as RDF/Turtle: ' . dataset_file($dataset .'.ttl', $files) . '</li>';
    echo '    <li>as N-Triples: ' . dataset_file($dataset .'.nt', $files) . '</li>';
    echo '  </ul></li>';
    echo '  <li>Core vocabulary as MARC21: ';
    echo dataset_file($dataset .'.marc21.xml', $files);
    echo '  </li>';
    echo '  <li>Core vocabulary + mappings:<ul>';
    echo '    <li>as RDF/Turtle: ' . dataset_file($dataset .'.complete.ttl', $files) . '</li>';
    echo '    <li>as N-Triples: ' . dataset_file($dataset .'.complete.nt', $files) . '</li>';
    echo '  </ul></li>';
    echo '  <li>Mappings as N-Triples:<ul>';
    echo dataset_files($files, "/\.mappings.nt$/");
    echo '  </ul></li>';

    // foreach ($files as $f) {
    //     echo '<li><a href="' . $f . '">' . $f . '</a> (' . $fsize . ')</li>';
    // }
    echo '</ul>';
}

?>
</div>



</body>
</html>

