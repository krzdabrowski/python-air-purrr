<?php 
if (isset($_GET['led1'])) {	
	if($_GET['led1'] == 1) {
		// $python = `python3 /home/pi/pro/main.py`;
		// echo $python;
		$command = escapeshellcmd('/home/pi/pro/main.py');
		$output = shell_exec($command);
		echo $output;
		
		print("led 1 has been activ4ted");
	} else {
		print("led1 has not been activated");
	}
}
if(isset($_GET['led2'])) {
	if($_GET['led2'] == 1) {
		$command = escapeshellcmd('/home/pi/pro/main.py');
		$output = shell_exec($command);
		echo $output;

		print("led 2 has been activated biacz");
	} else {
		print("led 2 is really off");
	}
}
?>
