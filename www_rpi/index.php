<?php

if( ! empty($_SERVER['HTTP_X_REQUESTED_WITH']) )
{
	if( strtolower($_SERVER['HTTP_X_REQUESTED_WITH']) == 'xmlhttprequest' )
	{
		if( ! empty($_GET['t']) && $_GET['t'] == 'get' )
		{
			$t = create_token();

			$html = '<table id="butttton-' . $t . '"><tr>
				<td align="center" valign="middle"><button id="butttton"></button></td></tr>
			</table>';

			echo json_encode(array('html' => $html, 't' => $t));
		}
		else if( ! empty($_POST['t']) )
		{
			$t = $_POST['t'];

			if( use_token($t) ) {
				add_click();
			}
		}

		exit();
	}
}

function use_token( $token )
{
	$found = false;
	$filename = 'tokens.php';

	if( ! @file_exists($filename) )	{
		$handle = @fopen($filename, 'wb');
		if( ! $handle ) { exit('Uh. Error creating file: ' . $filename); }
		fclose($handle);
		return false;
	}

	$handle = @fopen($filename, 'rb');

	if( ! $handle ) {
		exit('Uh. Error opening file for reading: ' . $filename);
	}

	$tempfilename = md5(microtime()) . '.tmp';
	$temphandle = fopen($tempfilename, 'wb');

	if( ! $temphandle ) {
		exit('Uh. Error opening file for writing: ' . $tempfilename);
	}

	while( ($line = fgets($handle)) !== false )
	{
		if( $line !== $token ) {
			fwrite($temphandle, $line);
		} else {
			$found = true;
		}
	}

	fclose($temphandle);
	fclose($handle);

	unlink($filename);
	rename($tempfilename, $filename);

	return $found;
}

function create_token()
{
	$filename = 'tokens.php';
	$handle = @fopen($filename, 'ab');
	$token = md5(microtime()) . "\n";

	if( ! $handle ) {
		exit('Uh. Error opening file for writing: ' . $filename);
	}

	fwrite($handle, $token);
	fclose($handle);

	return $token;
}

function add_click()
{
	/*
	// Bruno's original
	$filename = 'lastclicks.txt';
	$handle = @fopen($filename, 'ab');

	if( ! $handle ) {
		exit('Uh. Error opening file for writing: ' . $filename);
	}

	$datetime = date('Y-m-d H:i:s');
	$ip_address = get_user_ip_address();
	$str = $datetime . ', ' . $ip_address . "\n";

	fwrite($handle, $str);
	fclose($handle);

	return true;
	*/

	// Luis' messing stuff up with the intention of triggering Arduino
	$out = system("nodebang", $retval);
	if($retval != 0) {
		error_log("(!!!) something went wrong calling nodebang: ".$out);
	}
} // add_click

function get_user_ip_address()
{
	if( ! isset($_SERVER['HTTP_X_FORWARDED_FOR']) )
		$_SERVER['HTTP_X_FORWARDED_FOR'] = "";

	if( ! isset($_SERVER['HTTP_CLIENT_IP']) )
		$_SERVER['HTTP_CLIENT_IP'] = "";

	$ip_data = array
	(
		$_SERVER['HTTP_X_FORWARDED_FOR'],
		getenv('HTTP_X_FORWARDED_FOR'),
		$_SERVER['HTTP_CLIENT_IP'],
		getenv('HTTP_CLIENT_IP'),
		$_SERVER['REMOTE_ADDR'],
		getenv('REMOTE_ADDR'),
	);

	foreach($ip_data as $ip)
	{
		if( !empty($ip) && '192' != substr($ip, 0, 3) && '127' != substr($ip, 0, 3) )
		{
			$ip_address = $ip;
			break;
		}
	}

	if( !isset($ip_address) ) {
		return '0.0.0.0';
	}

	return $ip_address;
}

?>
<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<title>Butttton</title>
	<style>
		html,
		body
		{
			height: 100%;
			margin: 0;
			background: #000;
		}

		body.done
		{
			background: #FFF;
		}

		#butttton
		{
			display: inline-block;
			width: 200px;
			height: 200px;
			border: none;
			outline: none;
			border-radius: 50%;
			background: #FFF;
			cursor: pointer;
			opacity: 0;

			transition: all 0.5s;
		}

		.ready #butttton
		{
			opacity: 1;
		}
	
		#butttton:hover
		{
			width: 220px;
			height: 220px;
		}

		.done #butttton
		{
			background: #000;
			width: 140px;
			height: 140px;
		}

		.done #butttton:hover
		{
			width: 200px;
			height: 200px;
			cursor: default;
		}

		#content,
		table
		{
			width:100%;
			height: 100%;
		}
	</style>
</head>
<body>
	<div id="content">
	</div>
	<script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
	<script>

		jQuery(document).ready(function()
		{
			var $body = jQuery("body");
			var $content = jQuery("#content");
			var $button = jQuery("#butttton");
			var pauseMsAfterClick = 2000;

			function errFunc (err) {
				console.log(err);
			};

			function registerClick (data)
			{
				$button.attr("disabled", true);
				$body.addClass("done");

				setTimeout(function ()
				{
					$button.attr("disabled", false);
					$body.removeClass("done");
					start();
				}, pauseMsAfterClick);
			}

			function enableClick (data)
			{
				if( data && data.html )
				{
					if( $button.length > 0 )
					{
						$button.parents("table").attr("id", "butttton-" + data.t);
					}
					else
					{
						$content.append(data.html);
						$button = jQuery("#butttton");

						$button.on("click", function(event)
						{
							event.preventDefault();

							jQuery.ajax({
								type: "POST",
								url: "index.php",
								data: {
									t: $button.data("token")
								}
							})
							.success(registerClick)
							.error(errFunc);
						});

						setTimeout(function () {
							$body.addClass("ready");		
						}, 0);
					}

					$button.data("token", data.t)
				}
			}

			function start ()
			{
				jQuery.ajax({
					type: "GET",
					dataType: "json",
					url: "index.php",
					data: {
						t: "get"
					}
				})
				.success(enableClick)
				.error(errFunc);
			}

			start();
		});
			
	</script>
</body>
</html>
