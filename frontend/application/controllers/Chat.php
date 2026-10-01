<?php
defined('BASEPATH') OR exit('No direct script access allowed');

class Chat extends CI_Controller {

    public function __construct() {
        parent::__construct();
        $this->load->library('fastapi_client');
    }

    public function index() {
        $data['active_page'] = 'chat';
        $data['page_title'] = 'AI Financial Invoicing Assistant (RAG & Tools)';

        $this->load->view('templates/header', $data);
        $this->load->view('chat/index', $data);
        $this->load->view('templates/footer', $data);
    }

    public function send_message() {
        header('Content-Type: application/json');

        $raw_input = file_get_contents('php://input');
        $payload = json_decode($raw_input, true);

        if (!$payload) {
            $payload = $this->input->post();
        }

        $query = isset($payload['query']) ? trim($payload['query']) : '';
        $session_id = isset($payload['session_id']) ? $payload['session_id'] : 'session_' . session_id();

        if (empty($query)) {
            echo json_encode(array('success' => false, 'message' => 'Query cannot be empty'));
            return;
        }

        $api_payload = array(
            'query' => $query,
            'session_id' => $session_id
        );

        $res = $this->fastapi_client->post('/api/chat', $api_payload);

        if ($res['success']) {
            echo json_encode(array(
                'success' => true,
                'data' => $res['data']
            ));
        } else {
            $err = isset($res['data']['detail']) ? $res['data']['detail'] : ($res['error'] ?: 'AI chat service unavailable');
            echo json_encode(array(
                'success' => false,
                'message' => $err
            ));
        }
    }
}
