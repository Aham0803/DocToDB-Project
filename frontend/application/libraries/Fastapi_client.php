<?php
defined('BASEPATH') OR exit('No direct script access allowed');

class Fastapi_client {

    protected $CI;
    protected $base_url;
    protected $api_key;
    protected $timeout;

    public function __construct() {
        $this->CI =& get_instance();
        $this->CI->load->config('api_config', TRUE);
        
        $this->base_url = rtrim($this->CI->config->item('fastapi_base_url', 'api_config'), '/');
        $this->api_key  = $this->CI->config->item('fastapi_api_key', 'api_config');
        $this->timeout  = $this->CI->config->item('fastapi_timeout', 'api_config') ?: 60;
    }

    /**
     * Send GET request
     */
    public function get($endpoint, $params = array()) {
        $url = $this->base_url . '/' . ltrim($endpoint, '/');
        if (!empty($params)) {
            $url .= '?' . http_build_query($params);
        }

        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, $this->timeout);
        curl_setopt($ch, CURLOPT_HTTPHEADER, array(
            'X-API-Key: ' . $this->api_key,
            'Accept: application/json'
        ));

        $response = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $curl_error = curl_error($ch);
        curl_close($ch);

        if ($curl_error) {
            return array('success' => false, 'error' => $curl_error, 'data' => null);
        }

        return array(
            'success' => ($http_code >= 200 && $http_code < 300),
            'http_code' => $http_code,
            'data' => json_decode($response, true)
        );
    }

    /**
     * Send POST request with JSON payload
     */
    public function post($endpoint, $data = array()) {
        $url = $this->base_url . '/' . ltrim($endpoint, '/');
        $json_payload = json_encode($data);

        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $json_payload);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, $this->timeout);
        curl_setopt($ch, CURLOPT_HTTPHEADER, array(
            'X-API-Key: ' . $this->api_key,
            'Content-Type: application/json',
            'Accept: application/json'
        ));

        $response = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $curl_error = curl_error($ch);
        curl_close($ch);

        if ($curl_error) {
            return array('success' => false, 'error' => $curl_error, 'data' => null);
        }

        return array(
            'success' => ($http_code >= 200 && $http_code < 300),
            'http_code' => $http_code,
            'data' => json_decode($response, true)
        );
    }

    /**
     * Upload File via Multipart POST
     */
    public function upload_file($file_path, $original_filename, $mime_type, $provider = null) {
        $url = $this->base_url . '/api/documents/upload';

        if (function_exists('curl_file_create')) {
            $cfile = curl_file_create($file_path, $mime_type, $original_filename);
        } else {
            $cfile = '@' . realpath($file_path);
        }

        $post_data = array('file' => $cfile);
        if ($provider) {
            $post_data['provider'] = $provider;
        }

        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $post_data);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 90);
        curl_setopt($ch, CURLOPT_HTTPHEADER, array(
            'X-API-Key: ' . $this->api_key,
            'Accept: application/json'
        ));

        $response = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $curl_error = curl_error($ch);
        curl_close($ch);

        if ($curl_error) {
            return array('success' => false, 'error' => $curl_error, 'data' => null);
        }

        return array(
            'success' => ($http_code >= 200 && $http_code < 300),
            'http_code' => $http_code,
            'data' => json_decode($response, true)
        );
    }
}
