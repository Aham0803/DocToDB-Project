<?php
defined('BASEPATH') OR exit('No direct script access allowed');

class CI_Controller {

    private static $instance;
    public $load;
    public $input;
    public $config;
    public $uri;

    public function __construct() {
        self::$instance =& $this;
        $this->load = new CI_Loader();
        $this->input = new CI_Input();
        $this->config =& $GLOBALS['CFG'];
        $this->uri =& $GLOBALS['URI'];

        // Autoload helpers and libraries
        if (file_exists(APPPATH.'config/autoload.php')) {
            require APPPATH.'config/autoload.php';
            if (isset($autoload['helper']) && is_array($autoload['helper'])) {
                $this->load->helper($autoload['helper']);
            }
            if (isset($autoload['libraries']) && is_array($autoload['libraries'])) {
                foreach ($autoload['libraries'] as $lib) {
                    $this->load->library($lib);
                }
            }
        }
    }

    public static function &get_instance() {
        return self::$instance;
    }
}
