<?php 
if (isset($_GET['led1'])) {	
	if($_GET['led1'] == 1) {
		$command = escapeshellcmd('/home/pi/testy/example.py');
		$output = shell_exec($command);
		echo $output;
	} else {
		$command = escapeshellcmd('touch /home/pi/testy/USUNTO.py');
		$output = shell_exec($command);
		echo $output;
	}
}
if(isset($_GET['led2'])) {
	if($_GET['led2'] == 1) {
		$command = escapeshellcmd('/home/pi/skrypt_manual_on.py');
		$output = shell_exec($command);
		echo $output;
	} else {
		$command = escapeshellcmd('/home/pi/skrypt_manual_off.py');
		$output = shell_exec($command);
		echo $output;
	}
}
?>