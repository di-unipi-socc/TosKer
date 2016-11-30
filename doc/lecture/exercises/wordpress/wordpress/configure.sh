#!/bin/sh
cp wp-config-sample.php wp-config.php

sed -i 's/localhost/mysql_container/' wp-config.php
sed -i 's/username_here/root/' wp-config.php
sed -i 's/password_here/password/' wp-config.php
sed -i 's/database_name_here/wordpress_db/' wp-config.php
