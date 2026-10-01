<?php
defined('BASEPATH') OR exit('No direct script access allowed');

class CI_URI {
    public $uri_string = '';
    public $segments = array();

    public function __construct() {
        $uri = isset($_SERVER['REQUEST_URI']) ? $_SERVER['REQUEST_URI'] : '';
        // Strip query string
        if (($pos = strpos($uri, '?')) !== FALSE) {
            $uri = substr($uri, 0, $pos);
        }
        // Strip script name if executed as subfolder
        $script_name = isset($_SERVER['SCRIPT_NAME']) ? $_SERVER['SCRIPT_NAME'] : '';
        $base_folder = dirname($script_name);
        if ($base_folder !== '/' && $base_folder !== '\\' && strpos($uri, $base_folder) === 0) {
            $uri = substr($uri, strlen($base_folder));
        }

        $this->uri_string = trim($uri, '/');
        $this->segments = ($this->uri_string === '') ? array() : explode('/', $this->uri_string);
    }

    public function segment($n, $no_result = NULL) {
        return isset($this->segments[$n - 1]) ? $this->segments[$n - 1] : $no_result;
    }
}
