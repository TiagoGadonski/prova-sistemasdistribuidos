<?php
require 'vendor/autoload.php';
$dotenv = Dotenv\Dotenv::createImmutable(__DIR__);
$dotenv->load();

use PhpAmqpLib\Connection\AMQPStreamConnection;
use PhpAmqpLib\Message\AMQPMessage;

$uri      = parse_url($_SERVER['REQUEST_URI']);
$method   = $_SERVER['REQUEST_METHOD'];

if ($uri['path'] === '/equipments' && $method === 'GET') {
    header('Content-Type: application/json');
    echo json_encode([
        ["id" => 1, "name" => "Bomba Submersível"],
        ["id" => 2, "name" => "Válvula de Segurança"],
        ["id" => 3, "name" => "Mangueira Alta Pressão"]
    ]);
    exit;
}

if ($uri['path'] === '/dispatch' && $method === 'POST') {
    $body = file_get_contents('php://input');
    $conn = AMQPStreamConnection::create_connection([AMQPStreamConnection::parse_url($_ENV['RABBIT_URL'])]);
    $ch   = $conn->channel();
    $ch->queue_declare($_ENV['QUEUE'], false, true, false, false);
    $msg  = new AMQPMessage($body, ['delivery_mode' => AMQPMessage::DELIVERY_MODE_PERSISTENT]);
    $ch->basic_publish($msg, '', $_ENV['QUEUE']);
    $ch->close(); $conn->close();

    header('Content-Type: application/json', true, 202);
    echo json_encode(["msg" => "Despacho enviado à fila"]);
    exit;
}

http_response_code(404);
echo "Not Found";
