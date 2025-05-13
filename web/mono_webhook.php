<?php
$DATA_FILE = 'transactions.txt';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = file_get_contents('php://input');
    file_put_contents($DATA_FILE, $data . "\n", FILE_APPEND);
    http_response_code(200); 
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    http_response_code(200);
    exit;
}
