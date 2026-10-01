<?php
defined('BASEPATH') OR exit('No direct script access allowed');

require_once BASEPATH.'core/Common.php';
require_once BASEPATH.'core/Config.php';
require_once BASEPATH.'core/URI.php';
require_once BASEPATH.'core/Router.php';
require_once BASEPATH.'core/Input.php';
require_once BASEPATH.'core/Loader.php';
require_once BASEPATH.'core/Controller.php';

// Global instances
$GLOBALS['CFG'] = new CI_Config();
$GLOBALS['URI'] = new CI_URI();
$GLOBALS['RTR'] = new CI_Router();

$URI =& $GLOBALS['URI'];
$RTR =& $GLOBALS['RTR'];

// Route request
$RTR->parse_route($URI->uri_string);

$class = $RTR->class;
$method = $RTR->method;
$params = $RTR->params;

$controller_file = APPPATH.'controllers/'.$class.'.php';
if (!file_exists($controller_file)) {
    show_404($class.'/'.$method);
}

require_once $controller_file;

if (!class_exists($class, FALSE) || !method_exists($class, $method)) {
    show_404($class.'/'.$method);
}

$CI = new $class();
call_user_func_array(array($CI, $method), $params);
