<?php
	$id = $_GET['id'];
	$signal = $_GET['signal'];

	if ($id == "garden") {
		$si_humidity = $_GET['si_humidity'];
		$si_temperature = $_GET['si_temperature'];
		$dallas_2m = $_GET['dallas_2m'];
		$dallas_5cm = $_GET['dallas_5cm'];
		if (!is_nan($si_humidity)) {
			$si_humidity = "---";
		}
		if (!is_nan($si_temperature)) {
			$si_temperature = "---";
		}
		if ($dallas_2m == "85.00" || $dallas_2m == "-127.00") {
			$dallas_2m = "---";
		}
		if ($dallas_5cm == "85.00" || $dallas_5cm == "-127.00") {
			$dallas_5cm = "---";
		}
		$garden_file = fopen('/tmp/esp8266_'.$id, 'w');
		fwrite($garden_file, time().PHP_EOL);
		fwrite($garden_file, $signal.PHP_EOL);
		fwrite($garden_file, $si_humidity.PHP_EOL);
		fwrite($garden_file, $si_temperature.PHP_EOL);
		fwrite($garden_file, $dallas_2m.PHP_EOL);
		fwrite($garden_file, $dallas_5cm.PHP_EOL);
		fclose($garden_file);
	}

?>
