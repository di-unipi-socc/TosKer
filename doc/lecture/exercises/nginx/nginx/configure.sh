#!/bin/sh
sed -i '1s/daemon off;//' /etc/nginx/nginx.conf
sed -i '1s/^/daemon off;\n/' /etc/nginx/nginx.conf
sed -i "s/listen 80/listen $INPUT_PORT/" /etc/nginx/sites-available/default
