<?php
defined('BASEPATH') OR exit('No direct script access allowed');

class Documents extends CI_Controller {

    public function __construct() {
        parent::__construct();
        $this->load->library('fastapi_client');
    }

    public function upload() {
        $data['active_page'] = 'upload';
        $data['page_title'] = 'Upload GST Invoices & Bills';

        $this->load->view('templates/header', $data);
        $this->load->view('documents/upload', $data);
        $this->load->view('templates/footer', $data);
    }

    public function ajax_upload() {
        header('Content-Type: application/json');

        if (empty($_FILES['file']['name'])) {
            echo json_encode(array('success' => false, 'message' => 'No file uploaded'));
            return;
        }

        $file_tmp = $_FILES['file']['tmp_name'];
        $file_name = $_FILES['file']['name'];
        $mime_type = $_FILES['file']['type'];
        $provider = $this->input->post('provider') ?: null;

        $response = $this->fastapi_client->upload_file($file_tmp, $file_name, $mime_type, $provider);

        if ($response['success']) {
            $doc_data = $response['data'];
            $doc_id = isset($doc_data['document_id']) ? $doc_data['document_id'] : '';
            $status = isset($doc_data['status']) ? $doc_data['status'] : '';

            $redirect_url = base_url('invoices');
            if ($status === 'PENDING_REVIEW') {
                $redirect_url = base_url('review/verify/' . $doc_id);
            } elseif ($status === 'DUPLICATE') {
                $redirect_url = base_url('queue');
            }

            echo json_encode(array(
                'success' => true,
                'document_id' => $doc_id,
                'status' => $status,
                'redirect_url' => $redirect_url,
                'message' => 'Invoice processed via LangGraph pipeline: ' . $status
            ));
        } else {
            $err_msg = isset($response['data']['detail']) ? $response['data']['detail'] : ($response['error'] ?: 'FastAPI backend connection failure');
            echo json_encode(array(
                'success' => false,
                'message' => $err_msg
            ));
        }
    }
}
