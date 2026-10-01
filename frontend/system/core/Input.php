<?php
defined('BASEPATH') OR exit('No direct script access allowed');

class CI_Input {
    public function get($index = NULL) {
        if ($index === NULL) return $_GET;
        return isset($_GET[$index]) ? $_GET[$index] : NULL;
    }

    public function post($index = NULL) {
        if ($index === NULL) return $_POST;
        return isset($_POST[$index]) ? $_POST[$index] : NULL;
    }

    public function server($index = NULL) {
        if ($index === NULL) return $_SERVER;
        return isset($_SERVER[$index]) ? $_SERVER[$index] : NULL;
    }

    public function is_ajax_request() {
        return (isset($_SERVER['HTTP_X_REQUESTED_WITH']) && strtolower($_SERVER['HTTP_X_REQUESTED_WITH']) === 'xmlhttprequest');
    }
}
