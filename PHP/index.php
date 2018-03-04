<?php 
if (isset($_GET['AUTO'])) {	
	if($_GET['AUTO'] == 1) {
		$command = escapeshellcmd('/home/pi/skrypt_on.py');
		$output = shell_exec($command);
		echo $output;
	} else {
		$command = escapeshellcmd('/home/pi/skrypt_off.py');
		$output = shell_exec($command);
		echo $output;
	}
}
if(isset($_GET['MANUAL'])) {
	if($_GET['MANUAL'] == 1) {
		$command = escapeshellcmd('/home/pi/skrypt_on.py');
		$output = shell_exec($command);
		echo $output;
	} else {
		$command = escapeshellcmd('/home/pi/skrypt_off.py');
		$output = shell_exec($command);
		echo $output;
	}
}
?>