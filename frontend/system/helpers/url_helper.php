<?php
defined('BASEPATH') OR exit('No direct script access allowed');

if (!function_exists('base_url')) {
    function base_url($uri = '') {
        $CI =& get_instance();
        return $CI->config->base_url($uri);
    }
}

if (!function_exists('site_url')) {
    function site_url($uri = '') {
        $CI =& get_instance();
        return $CI->config->site_url($uri);
    }
}

if (!function_exists('redirect')) {
    function redirect($uri = '', $method = 'auto', $code = NULL) {
        $url = (strpos($uri, '://') === FALSE) ? site_url($uri) : $uri;
        header("Location: ".$url, TRUE, $code ?: 302);
        exit;
    }
}
