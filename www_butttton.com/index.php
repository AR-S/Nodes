<!DOCTYPE html>
<html class="no-js">
<head>
       	<meta charset="utf-8">
       	<meta http-equiv="X-UA-Compatible" content="IE=edge">
       	<title>Butttton</title>
       	<style type="text/css">
       		body
       		{
       			margin: 0;
       			background: #000;
       			color: #FFF;
       		}

       		#notice,
       		#framed
       		{
       			position: absolute;
       			top: 0;
       			left: 0;
       			width: 100%;
       			height: 100%;
       			z-index: 1;
       			background: #000;
       		}

       		#notice
       		{
       			background-image: url(butttton_web_offline.png);
       			background-repeat: no-repeat;
       			background-position: center center;
       			background-size: contain;
       			opacity: 0;
       			transition: all 1s;
       		}

       		#framed
       		{
       			z-index: 2;
       		}

       		.no-js #framed
       		{
       			display: none;
       		}

       		.no-js #notice
       		{
       			background-image: none;
       			font-family: Helvetica, Arial, sans-serif;
       			text-align: center;
       			height: 24px;
       			top: 50%;
       			margin-top: -12px;
       			opacity: 1;
       		}

       		.offline #framed
       		{
       			display: none;
       		}

       		.offline #notice
       		{
       			opacity: 1;
       		}
       	</style>
</head>
<body>

       	<div id="notice">
       		<noscript>Butttton needs javascript, please enable it in your browser.</noscript>
       	</div>

       	<iframe id="framed"
       		src="http://ars-nodes.duckdns.org:8080"
       		frameborder="0"
       		width="100%"
       		height="100%">
       	</iframe>

       	<script type="text/javascript">
       		(function()
       		{
       			var doc = document.documentElement;
       			var xhr = new XMLHttpRequest();
       			var framed = document.getElementById("framed");

       			doc.className = "js";

       			xhr.ontimeout = function ()
       			{
       				doc.className = "js offline";
       				framed.parentNode.removeChild(framed);
       			};

       			xhr.onreadystatechange = function()
       			{
       				if( xhr.readyState === 4 )
       				{
       					if( xhr.status === 200 ) {
       						doc.className = "js online";
       					}
       					else
       					{
       						doc.className = "js offline";

       						if( xhr.statusText ) {
       							console.error(xhr.statusText);
       						}
       					}
       				}
       			};

       			xhr.timeout = 3000;
       			xhr.open("GET", framed.src, true);
       			xhr.send(null);
       		})();
       	</script>

</body>
</html>
