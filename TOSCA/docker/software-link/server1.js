/* jslint node: true */
"use strict";
var express = require('express');

var app = express();

app.get('/', function (req, res) {
    res.send('hello-world');
});

app.listen(process.env.PORT || 8081, function(){
    console.log('server listen..');
});
