<?php

require('vendor/autoload.php');

use Scriptotek\Sru\Client as SruClient;
use Scriptotek\Marc\Record;

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    header('Access-Control-Allow-Origin: *');
    header('Access-Control-Allow-Methods: GET');
    header('Access-Control-Allow-Headers: Content-Type');
    header('Content-Length: 0');
    header('Content-Type: text/plain');
    die();
}

header('Access-Control-Allow-Origin: *');

if (!isset($_GET['mms_id'])) {
    header('Content-Type: text/html; charset=utf-8');
    print '<p>Is the cat alive? Is the book on the shelf? Important questions of life that I can shed light on if you gimme <a href="http://data.ub.uio.no/microservices/availability.php?mms_id=991420796004702204"><tt>mms_id</tt></a>.';
    return;
}

// Remove anything non-numeric
$mms_id = preg_replace('/[^0-9.]/', '', $_GET['mms_id']);

$sru = new SruClient('http://bibsys-network.alma.exlibrisgroup.com/view/sru/47BIBSYS_UBO', [
    'schema' => 'marcxml',
    'version' => '1.2',
    'user-agent' => 'DeadCat/0.1',
]);

function error($msg) {
    http_response_code(400);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode(['error' => $msg], JSON_PRETTY_PRINT);
    exit;
}

$sru_rec = $sru->first('alma.mms_id="' . $mms_id . '"');

if (!$sru_rec) {
    error('The record was not found!');
}

$rec = Record::fromString($sru_rec->data->asXML());

if ($rec->getField('AVA')) {
    /*
    $$a - Institution code, $$b - Library code, $$c - Location display name, 
    $$d - Call number, $$e - Availability (such as available, unavailable, or check_holdings), 
    $$j - Location code, $$k - Call number type, $$f - total items, $$g - non available items, 
    $$p - priority, $$8 - Holdings ID, $$t - Holdings Information, $$q - library name.
    */
    $data = [
        'carrier' => 'physical',
        'mms_id' => $rec->query('AVA$0')->text(),
        'holdings_id' => $rec->query('AVA$8')->text(),
        'holdings_info' => $rec->query('AVA$t')->text(),

        'institution_code' => $rec->query('AVA$a')->text(),
        'library_code' => $rec->query('AVA$b')->text(),
        'library_name' => $rec->query('AVA$q')->text(),
        'location_name' => $rec->query('AVA$c')->text(),
        'location_code' => $rec->query('AVA$j')->text(),
        'call_code' => $rec->query('AVA$d')->text(),

        'availability' => $rec->query('AVA$e')->text(),
        'total_items' => $rec->query('AVA$f')->text(),
        'non_available_items' => $rec->query('AVA$g')->text(),
        'priority' => $rec->query('AVA$p')->text(),
    ];

} else if ($rec->getField('AVE')) {
    /* $$l - library code, $$m - Collection name, $$n - Public note, $$u - link to the bibliographic record's services page, 
    $$s - coverage statement (as displayed in Primo's ViewIt mashup), $$t - Interface name. 
    $$8 - portfolio pid, $$c - collection identifier for the electronic resource, $$e - activation status. 

    */
    $data = [
        'carrier' => 'electronic',

        'library_code' => $rec->query('AVE$l')->text(),
        'collection_name' => $rec->query('AVE$m')->text(),
        'public_note' => $rec->query('AVE$n')->text(),
        'link' => $rec->query('AVE$u')->text(),
        'coverage' => $rec->query('AVE$s')->text(),
        'interface_name' => $rec->query('AVE$t')->text(),
        'portfolio_pid' => $rec->query('AVE$8')->text(),
        'collection_id' => $rec->query('AVE$c')->text(),
        'activation_status' => $rec->query('AVE$e')->text(),
    ];

} else if ($rec->getField('AVD')) {
    /* $$a - Institution code, $$b - Representations ID, $$c - REPRESENTATION/REMOTE_REPRESENTATION, $$d - Repository Name, $$e - Label, */
    
    $data = [
        'carrier' => 'digital',

        'institution_code' => $rec->query('AVD$a')->text(),
        'representations_id' => $rec->query('AVD$b')->text(),
        'representation' => $rec->query('AVD$c')->text(),
        'repository_name' => $rec->query('AVD$d')->text(),
        'label' => $rec->query('AVD$e')->text(),
    ];

} else {
    error('Found no availability info for this record, perhaps there\'s no holdings?');
}

if (isset($_GET['marc'])) {
    header('Content-Type: text/plain; charset=utf-8');
    echo (string) $rec;
    exit;
}

header('Content-Type: application/json; charset=utf-8');
echo json_encode($data, JSON_PRETTY_PRINT);
exit;

