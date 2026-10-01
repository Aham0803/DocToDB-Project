<?php
defined('BASEPATH') OR exit('No direct script access allowed');

class CI_Config {

    public $config = array();
    public $is_loaded = array();

    public function __construct() {
        if (file_exists(APPPATH.'config/config.php')) {
            require APPPATH.'config/config.php';
            $this->config = isset($config) ? $config : array();
            $this->is_loaded['config.php'] = TRUE;
        }
    }

    public function load($file = '', $use_sections = FALSE, $fail_gracefully = FALSE) {
        $file = ($file === '') ? 'config' : str_replace('.php', '', $file);
        $file_path = APPPATH.'config/'.$file.'.php';

        if (file_exists($file_path)) {
            require $file_path;
            if (isset($config) && is_array($config)) {
                if ($use_sections === TRUE) {
                    $this->config[$file] = isset($this->config[$file]) ? array_merge($this->config[$file], $config) : $config;
                } else {
                    $this->config = array_merge($this->config, $config);
                }
            }
            $this->is_loaded[$file] = TRUE;
            return TRUE;
        }

        if ($fail_gracefully === TRUE) {
            return FALSE;
        }
        show_error('The configuration file '.$file.'.php does not exist.');
    }

    public function item($item, $index = '') {
        if ($index == '') {
            return isset($this->config[$item]) ? $this->config[$item] : NULL;
        }
        return isset($this->config[$index][$item]) ? $this->config[$index][$item] : NULL;
    }

    public function base_url($uri = '') {
        $base_url = isset($this->config['base_url']) ? $this->config['base_url'] : '/';
        return rtrim($base_url, '/').'/'.ltrim($uri, '/');
    }

    public function site_url($uri = '') {
        return $this->base_url($uri);
    }
}
