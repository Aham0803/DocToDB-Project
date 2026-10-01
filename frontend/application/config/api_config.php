<?php
defined('BASEPATH') OR exit('No direct script access allowed');

/*
|--------------------------------------------------------------------------
| FastAPI Backend Integration Configuration
|--------------------------------------------------------------------------
*/

$config['fastapi_base_url'] = getenv('FASTAPI_BASE_URL') ? getenv('FASTAPI_BASE_URL') : 'http://127.0.0.1:8000';
$config['fastapi_api_key']  = getenv('API_SECRET_KEY') ? getenv('API_SECRET_KEY') : 'doctodb_secret_api_key_2026_secure';
$config['fastapi_timeout']  = 60; // seconds for heavy multimodal extraction
