<?php

    $localt = localtime(time(), true);
    $localt['time'] = time();
    echo(json_encode($localt));

?>

