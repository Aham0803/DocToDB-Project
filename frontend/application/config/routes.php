<?php
defined('BASEPATH') OR exit('No direct script access allowed');

$route['default_controller'] = 'dashboard';
$route['404_override'] = '';
$route['translate_uri_dashes'] = FALSE;

// Clean SEO-friendly routes
$route['upload']             = 'documents/upload';
$route['upload/ajax']        = 'documents/ajax_upload';
$route['queue']              = 'review/index';
$route['review/verify/(:any)'] = 'review/verify/$1';
$route['review/submit/(:any)'] = 'review/submit/$1';
$route['invoices']           = 'invoices/index';
$route['invoices/view/(:num)'] = 'invoices/view/$1';
$route['invoices/export']    = 'invoices/export_csv';
$route['chat']               = 'chat/index';
$route['chat/send']          = 'chat/send_message';
