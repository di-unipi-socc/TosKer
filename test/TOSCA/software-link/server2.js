/* jslint node: true */
"use strict";
var express = require('express');

var app = express();

app.get('/', function (req, res) {
    res.send('hi! from server2');
});

app.listen(process.env.PORT || 80, function(){
  console.log('server listen on port ' + (process.env.PORT || 80));
});
