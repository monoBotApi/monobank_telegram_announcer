<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

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
    if (file_exists($DATA_FILE)) {
        $fp = fopen($DATA_FILE, 'r');
        if ($fp) {
            $line = null;
            if (flock($fp, LOCK_SH)) {
                $lines = [];
                while (($buffer = fgets($fp)) !== false) {
                    $lines[] = trim($buffer);
                }
                flock($fp, LOCK_UN);
                $lines = array_filter($lines, function ($l) { return $l !== ''; });
                if (!empty($lines)) {
                    header('Content-Type: application/json');
                    echo end($lines);
                    fclose($fp);
                    exit;
                }
            }
            fclose($fp);
        }
    }

    header('Content-Type: application/json');
    echo '{}';
    exit;
}
