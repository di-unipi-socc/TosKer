#!/bin/sh
TARGET=/thinking-gui/public/script/config/rest-api.js
echo apiUrl='"'$INPUT_APIURL'"' > $TARGET
echo apiPort='"'$INPUT_APIPORT'"' >> $TARGET
echo apiResource='"'$INPUT_APIRESOURCE'"' >> $TARGET

# add index.html that redirect to thoughts.html page.
echo '<html>
<head><meta http-equiv="refresh" content="0; url=/thoughts.html"/></head>
<body><p><a href="/thoughts.html">Redirect</a></p></body>
</html>' > /thinking-gui/public/index.html
