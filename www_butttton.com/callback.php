<?php
/*
 * The raspberry pi will try to call back on this URL to let us know
 * about its internal state once it's plugged on the network. We simply
 * save what the Rpi submitted to a text file.
 */
if( isset($_POST) ) {
        file_put_contents("rpicfg.txt", serialize($_POST) );
} else {
        file_put_contents("rpicfg.txt", "The Rpi hasn't called home yet!");
}
?>
