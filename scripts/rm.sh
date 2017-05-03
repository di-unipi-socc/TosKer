#!/bin/sh
base=$(dirname $0)
./$base/rm_containers.sh
./$base/rm_images.sh
./$base/rm_volumes.sh
./$base/rm_networks.sh
