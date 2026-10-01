<?php
defined('BASEPATH') OR exit('No direct script access allowed');

class Dashboard extends CI_Controller {

    public function __construct() {
        parent::__construct();
        $this->load->library('fastapi_client');
    }

    public function index() {
        $stats_res = $this->fastapi_client->get('/api/stats');
        $queue_res = $this->fastapi_client->get('/api/documents/queue');
        $invoices_res = $this->fastapi_client->get('/api/invoices', array('limit' => 5));

        $data['stats'] = ($stats_res['success'] && isset($stats_res['data'])) ? $stats_res['data'] : array(
            'total_documents' => 0,
            'auto_approved_count' => 0,
            'auto_approved_percent' => 0,
            'pending_review_count' => 0,
            'total_invoices_in_db' => 0,
            'total_grand_amount' => 0,
            'total_tax_amount' => 0
        );

        $data['pending_queue'] = ($queue_res['success'] && is_array($queue_res['data'])) ? array_slice($queue_res['data'], 0, 5) : array();
        $data['recent_invoices'] = ($invoices_res['success'] && isset($invoices_res['data']['invoices'])) ? $invoices_res['data']['invoices'] : array();
        $data['active_page'] = 'dashboard';
        $data['page_title'] = 'GST Invoice Intelligence Dashboard';

        $this->load->view('templates/header', $data);
        $this->load->view('dashboard/index', $data);
        $this->load->view('templates/footer', $data);
    }
}
