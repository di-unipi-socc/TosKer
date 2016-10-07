/* jslint node: true */
"use strict";
var express = require('express');
var bodyParser = require('body-parser');

var app = express();

app.use(bodyParser.urlencoded({extended: true}));
app.use(bodyParser.json());
app.use(bodyParser.json({type: 'application/vnd.api+json'}));

var http = require('http');

app.get('/', function (req, res) { //  /api
    var path = '/' + (req._parsedUrl.search || '');
    console.log("\nRedirect to images_server: " +path);

    var reqApi = http.request({
            host: process.env.SERVER_NAME || 'server1',
            // host: 'images_server',
            path: path,
            port: '8081',
            method: 'GET'
        },
        function (resApi) {
            res.writeHead(resApi.statusCode);
            resApi.pipe(res);
            console.log("Response received from images_server");
        }
    );
    reqApi.end();
});

app.listen(process.env.PORT || 8082, function(){
    console.log('server listen on port ' + (process.env.PORT || 8082));
});
