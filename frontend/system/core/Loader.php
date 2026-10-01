<?php
defined('BASEPATH') OR exit('No direct script access allowed');

class CI_Loader {

    public function view($view, $vars = array(), $return = FALSE) {
        $view_path = VIEWPATH.ltrim($view, '/').'.php';
        if (!file_exists($view_path)) {
            show_error('Unable to load the requested view file: '.$view);
            return;
        }

        if (is_array($vars)) {
            extract($vars);
        }

        ob_start();
        include $view_path;
        $buffer = ob_get_contents();
        ob_end_clean();

        if ($return === TRUE) {
            return $buffer;
        }

        echo $buffer;
    }

    public function library($library, $params = NULL, $object_name = NULL) {
        if (empty($library)) return;

        $lib_name = ucfirst(strtolower($library));
        $class_file = APPPATH.'libraries/'.$lib_name.'.php';

        if (file_exists($class_file)) {
            require_once $class_file;
            $obj_name = $object_name ? $object_name : strtolower($library);
            $CI =& get_instance();
            $CI->$obj_name = new $lib_name($params);
            return;
        }

        // Check system libraries (session, etc.)
        if (strtolower($library) === 'session') {
            if (session_status() === PHP_SESSION_NONE) {
                @session_start();
            }
            $CI =& get_instance();
            $CI->session = new stdClass();
            return;
        }
    }

    public function helper($helpers = array()) {
        if (!is_array($helpers)) {
            $helpers = array($helpers);
        }

        foreach ($helpers as $helper) {
            $helper_file = BASEPATH.'helpers/'.$helper.'_helper.php';
            if (file_exists($helper_file)) {
                require_once $helper_file;
            } elseif (file_exists(APPPATH.'helpers/'.$helper.'_helper.php')) {
                require_once APPPATH.'helpers/'.$helper.'_helper.php';
            }
        }
    }

    public function config($file = '', $use_sections = FALSE, $fail_gracefully = FALSE) {
        $CI =& get_instance();
        return $CI->config->load($file, $use_sections, $fail_gracefully);
    }
}
