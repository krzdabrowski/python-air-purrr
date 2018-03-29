<?php

session_start();
read_file();

function login() {
    header("WWW-Authenticate: Basic"); 
    header("HTTP/1.0 401 Unauthorized");
    die; 
}

function work() {
    if ($_POST) {	
	if($_POST["req"] == "MANUAL=1" || $_POST["req"] == "AUTO=1") {
		$command = escapeshellcmd('/home/pi/script_on.py');
		$output = shell_exec($command);
		echo $output;
	} else {
		$command = escapeshellcmd('/home/pi/script_off.py');
		$output = shell_exec($command);
		echo $output;
	}
    }
}

function read_file() {
    $data = explode("\n", file_get_contents('/home/pi/Desktop/db.txt'));
    return $data;
}


// auth
if (!isset($_SESSION["AUTH_SUCCESS"])) {
    $_SESSION["AUTH_SUCCESS"] = 0;
}
if ($_SESSION["AUTH_SUCCESS"] == 0) {
    $user = read_file()[0]; 
    $pass = read_file()[1];

    if ($_SERVER["PHP_AUTH_USER"] != $user || $_SERVER["PHP_AUTH_PW"] != $pass) { 
        login();
    } else {
        $_SESSION["AUTH_SUCCESS"] = 1;
	work();
    }
}
if ($_SESSION["AUTH_SUCCESS"] == 0) {
    die("You have entered a wrong password/username.");
}

?>