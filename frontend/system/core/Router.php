<?php
defined('BASEPATH') OR exit('No direct script access allowed');

class CI_Router {
    public $class = '';
    public $method = 'index';
    public $params = array();
    public $routes = array();

    public function __construct() {
        if (file_exists(APPPATH.'config/routes.php')) {
            require APPPATH.'config/routes.php';
            $this->routes = isset($route) ? $route : array();
        }
    }

    public function parse_route($uri_string) {
        // Default controller fallback
        if ($uri_string === '') {
            $default = isset($this->routes['default_controller']) ? $this->routes['default_controller'] : 'dashboard';
            $this->set_request(explode('/', $default));
            return;
        }

        // Check exact match
        if (isset($this->routes[$uri_string])) {
            $this->set_request(explode('/', $this->routes[$uri_string]));
            return;
        }

        // Regex pattern matching (e.g. (:any), (:num))
        foreach ($this->routes as $key => $val) {
            $pattern = str_replace(array(':any', ':num'), array('[^/]+', '[0-9]+'), $key);
            if (preg_match('#^'.$pattern.'$#', $uri_string, $matches)) {
                $target = preg_replace('#^'.$pattern.'$#', $val, $uri_string);
                $this->set_request(explode('/', $target));
                return;
            }
        }

        // Direct controller/method/params
        $segments = explode('/', $uri_string);
        $this->set_request($segments);
    }

    protected function set_request($segments) {
        $this->class = isset($segments[0]) ? ucfirst($segments[0]) : 'Dashboard';
        $this->method = isset($segments[1]) ? $segments[1] : 'index';
        $this->params = array_slice($segments, 2);
    }
}
