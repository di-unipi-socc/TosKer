#!/bin/sh

sed -i "s@/catalogue%s@/$INPUT_CATALOGUE%s@g" /front-end/api/endpoints.js
sed -i "s@/carts%s@/$INPUT_CARTS%s@g" /front-end/api/endpoints.js
sed -i "s@/orders%s@/$INPUT_ORDERS%s@g" /front-end/api/endpoints.js
sed -i "s@/user%s@/$INPUT_USER%s@g" /front-end/api/endpoints.js

#cat /front-end/api/endpoints.js
