#!/bin/bash

echo "Creating carts into /artifacts folder (carts.jar) ..."
cd ./helpers
source ./carts-build-jar.sh &> /dev/null
echo "Creating orders  into /artifacts folder (orders.jar) ......"
source ./orders-build-jar.sh &> /dev/null
echo "Creating shipping  into /artifacts folder (shipping.jar) ..."
source ./shipping-build-jar.sh &> /dev/null
