<?php
defined('BASEPATH') OR exit('No direct script access allowed');

// Form helper utility functions
if (!function_exists('form_open')) {
    function form_open($action = '', $attributes = array()) {
        $CI =& get_instance();
        $action = (strpos($action, '://') === FALSE) ? $CI->config->site_url($action) : $action;
        return '<form action="'.$action.'" method="post">';
    }
}

if (!function_exists('form_close')) {
    function form_close() {
        return '</form>';
    }
}
