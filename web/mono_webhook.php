<?php
$DATA_FILE = 'transactions.txt';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = file_get_contents('php://input');
    $fp = fopen($DATA_FILE, 'a');
    if ($fp) {
        if (flock($fp, LOCK_EX)) {
            fwrite($fp, $data . "\n");
            fflush($fp);
            flock($fp, LOCK_UN);
        }
        fclose($fp);
    }
    http_response_code(200); 
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    http_response_code(200);
    exit;
}
