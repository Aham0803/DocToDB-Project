<?php
defined('BASEPATH') OR exit('No direct script access allowed');

class Review extends CI_Controller {

    public function __construct() {
        parent::__construct();
        $this->load->library('fastapi_client');
        $this->load->helper('url');
    }

    public function index() {
        $status_filter = $this->input->get('status') ?: null;
        $params = $status_filter ? array('status_filter' => $status_filter) : array();
        $res = $this->fastapi_client->get('/api/documents/queue', $params);

        $data['queue_items'] = ($res['success'] && is_array($res['data'])) ? $res['data'] : array();
        $data['status_filter'] = $status_filter;
        $data['active_page'] = 'review';
        $data['page_title'] = 'Human-in-the-Loop Review Queue';

        $this->load->view('templates/header', $data);
        $this->load->view('review/index', $data);
        $this->load->view('templates/footer', $data);
    }

    public function verify($doc_id) {
        $res = $this->fastapi_client->get('/api/documents/' . $doc_id);
        if (!$res['success'] || empty($res['data'])) {
            show_error('Document not found or backend API unreachable', 404);
            return;
        }

        $doc = $res['data'];
        $data['document'] = $doc;
        $data['extracted'] = isset($doc['extracted_json']) ? $doc['extracted_json'] : array();
        $data['flags'] = isset($doc['flagged_reasons']) ? $doc['flagged_reasons'] : array();
        
        // Build document preview URL pointing to backend static uploads
        $this->load->config('api_config', TRUE);
        $backend_url = rtrim($this->config->item('fastapi_base_url', 'api_config'), '/');
        $data['file_url'] = $backend_url . '/' . ltrim($doc['stored_filepath'], '/');

        $data['active_page'] = 'review';
        $data['page_title'] = 'Verify & Correct Invoice: ' . htmlspecialchars($doc['original_filename']);

        $this->load->view('templates/header', $data);
        $this->load->view('review/verify', $data);
        $this->load->view('templates/footer', $data);
    }

    public function submit($doc_id) {
        header('Content-Type: application/json');

        $raw_input = file_get_contents('php://input');
        $payload = json_decode($raw_input, true);

        if (!$payload) {
            $payload = $this->input->post();
        }

        $reviewer_name = isset($payload['reviewer_name']) ? $payload['reviewer_name'] : 'accounts_officer';
        $corrected_data = isset($payload['corrected_data']) ? $payload['corrected_data'] : $payload;

        $api_payload = array(
            'reviewer_name' => $reviewer_name,
            'corrected_data' => $corrected_data
        );

        $res = $this->fastapi_client->post('/api/documents/' . $doc_id . '/review', $api_payload);

        if ($res['success']) {
            echo json_encode(array(
                'success' => true,
                'message' => 'Invoice verified and committed to MySQL successfully.',
                'redirect_url' => base_url('invoices')
            ));
        } else {
            $err = isset($res['data']['detail']) ? $res['data']['detail'] : ($res['error'] ?: 'Verification submission failed');
            echo json_encode(array(
                'success' => false,
                'message' => is_array($err) ? json_encode($err) : $err
            ));
        }
    }
}
