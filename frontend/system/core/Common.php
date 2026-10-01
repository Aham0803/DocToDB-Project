<?php
defined('BASEPATH') OR exit('No direct script access allowed');

if (!function_exists('get_instance')) {
    function &get_instance() {
        return CI_Controller::get_instance();
    }
}

if (!function_exists('is_php')) {
    function is_php($version) {
        static $_is_php;
        $version = (string) $version;
        if (!isset($_is_php[$version])) {
            $_is_php[$version] = version_compare(PHP_VERSION, $version, '>=');
        }
        return $_is_php[$version];
    }
}

if (!function_exists('log_message')) {
    function log_message($level, $message) {
        // Simple console/error_log fallback
        if (ENVIRONMENT === 'development') {
            error_log("[CI3 $level] $message");
        }
    }
}

if (!function_exists('show_error')) {
    function show_error($message, $status_code = 500, $heading = 'An Error Was Encountered') {
        header("HTTP/1.1 $status_code Service Error");
        echo "<div style='font-family: sans-serif; padding: 20px; background: #fff3f3; color: #b91c1c; border-radius: 8px; margin: 20px;'>";
        echo "<h2 style='margin-top:0;'>$heading</h2>";
        echo "<p>$message</p>";
        echo "</div>";
        exit(1);
    }
}

if (!function_exists('show_404')) {
    function show_404($page = '', $log_error = TRUE) {
        header('HTTP/1.1 404 Not Found');
        echo "<div style='font-family: sans-serif; padding: 20px; background: #fef2f2; color: #991b1b; border-radius: 8px; margin: 20px;'>";
        echo "<h2>404 Page Not Found</h2>";
        echo "<p>The requested page '$page' was not found on this server.</p>";
        echo "</div>";
        exit(1);
    }
}
