/* jslint node: true */
"use strict";
var express = require('express');
var bodyParser = require('body-parser');

var app = express();

app.use(bodyParser.urlencoded({
    extended: true
}));
app.use(bodyParser.json());

var http = require('http');
//
// app.get('/', function(req, res) { //  /api
//     var path = '/' + (req._parsedUrl.search || '');
//     console.log("\nRedirect to " + (process.env.SERVER_NAME || 'server1') + ' with path ' + path);
//
//     var reqApi = http.request({
//             host: process.env.SERVER_NAME || 'server1',
//             // host: 'images_server',
//             path: path,
//             port: '8081',
//             method: 'GET'
//         },
//         function(resApi) {
//             res.writeHead(resApi.statusCode);
//             resApi.pipe(res);
//             console.log("Response received!");
//         }
//     );
//     reqApi.end();
// });

app.get('/', function(req, res) {
    http.request({
            host: process.env.SERVER_NAME1 || 'server1',
            path: '/',
            port: '80',
            method: 'GET'
        },
        function(resApi1) {
            http.request({
                    host: process.env.SERVER_NAME2 || 'server2',
                    path: '/',
                    port: '80',
                    method: 'GET'
                },
                function(resApi2) {
                    res.writeHead(resApi1.statusCode);
                    resApi1.pipe(res);
                    resApi2.pipe(res);
                    console.log("Response received!");
                }
            ).end();
        }
    ).end();
});

app.listen(process.env.PORT || 80, function() {
    console.log('server listen on port ' + (process.env.PORT || 80));
});
