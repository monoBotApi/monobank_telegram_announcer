<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

$DATA_FILE = 'transactions.txt';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = file_get_contents('php://input');
    file_put_contents($DATA_FILE, $data . "\n", FILE_APPEND);
    http_response_code(200);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    if (file_exists($DATA_FILE)) {
        $lines = file($DATA_FILE, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
        if (!empty($lines)) {
            header('Content-Type: application/json');
            echo end($lines);
            exit;
        }
    }

    header('Content-Type: application/json');
    echo '{}';
    exit;
}
