<?php
defined('BASEPATH') OR exit('No direct script access allowed');

class Invoices extends CI_Controller {

    public function __construct() {
        parent::__construct();
        $this->load->library('fastapi_client');
    }

    public function index() {
        $search = $this->input->get('search') ?: null;
        $status = $this->input->get('status') ?: null;

        $params = array('limit' => 50);
        if ($search) $params['search'] = $search;
        if ($status) $params['payment_status'] = $status;

        $res = $this->fastapi_client->get('/api/invoices', $params);

        $data['invoices'] = ($res['success'] && isset($res['data']['invoices'])) ? $res['data']['invoices'] : array();
        $data['total_count'] = ($res['success'] && isset($res['data']['total'])) ? $res['data']['total'] : 0;
        $data['search'] = $search;
        $data['status_filter'] = $status;
        $data['active_page'] = 'invoices';
        $data['page_title'] = 'Verified MySQL GST Invoices';

        $this->load->view('templates/header', $data);
        $this->load->view('invoices/index', $data);
        $this->load->view('templates/footer', $data);
    }

    public function view($id) {
        $res = $this->fastapi_client->get('/api/invoices/' . intval($id));
        if (!$res['success'] || empty($res['data'])) {
            show_error('Invoice not found in database', 404);
            return;
        }

        $data['invoice'] = $res['data'];
        $data['active_page'] = 'invoices';
        $data['page_title'] = 'Invoice #' . htmlspecialchars($data['invoice']['invoice_number']);

        $this->load->view('templates/header', $data);
        $this->load->view('invoices/view', $data);
        $this->load->view('templates/footer', $data);
    }

    public function export_csv() {
        $res = $this->fastapi_client->get('/api/invoices', array('limit' => 500));
        $invoices = ($res['success'] && isset($res['data']['invoices'])) ? $res['data']['invoices'] : array();

        header('Content-Type: text/csv');
        header('Content-Disposition: attachment; filename="gst_invoices_export_' . date('Ymd_His') . '.csv"');

        $output = fopen('php://output', 'w');
        fputcsv($output, array('ID', 'Invoice Number', 'Date', 'Vendor Name', 'Vendor GSTIN', 'Customer Name', 'Subtotal (INR)', 'CGST', 'SGST', 'IGST', 'Total Tax', 'Grand Total (INR)', 'Status', 'Verification'));

        foreach ($invoices as $inv) {
            fputcsv($output, array(
                $inv['id'],
                $inv['invoice_number'],
                $inv['invoice_date'],
                $inv['vendor_name'],
                $inv['vendor_gstin'],
                $inv['customer_name'],
                $inv['subtotal'],
                $inv['cgst'],
                $inv['sgst'],
                $inv['igst'],
                $inv['total_tax'],
                $inv['grand_total'],
                $inv['payment_status'],
                $inv['verification_type']
            ));
        }
        fclose($output);
        exit;
    }
}
