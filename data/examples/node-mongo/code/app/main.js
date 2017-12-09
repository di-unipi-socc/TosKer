/* jslint node: true, esversion: 6 */
"use strict";
var express = require('express');
var mongoose = require('mongoose');

(function connect_to_mongo() {
    mongoose.connect(`mongodb://${process.env.DB || 'db'}/data1`, (err) => {
        if (err) {
            console.log('db not found');
            connect_to_mongo();
        } else {
            console.log('connection successful');
            if (process.argv.length < 3)
                run_server();
            else if (process.argv[2] == '--push-test-data')
                push_data(() => mongoose.disconnect());
        }
    });
})();

var Schema = mongoose.Schema;
var People = mongoose.model('People',
    new Schema({
        name: String,
        surname: String
    })
);

function run_server() {
    var app = express();

    app.get('/', function (req, res) {
        People.find(function (err, people) {
            var html = '<h3>People:</h3>';
            html += '<ul>';
            people.forEach(p => html += '<li>' + p.name + ' ' + p.surname + '</li>');
            html += '</ul>';
            res.send(html);
        });
    });

    var port = process.env.PORT || 80;
    app.listen(port, function () {
        console.log('server listen on port ' + port);
    });
}

function push_data(cb) {
    var data = require("./test_data.json");
    data.forEach((person, i, list) => {
        console.log(person);
        People.create(person, (err) => {
            if (err)
                return cb(err);
            if (i == list.length - 1)
                return cb(null);
        });
    });
}
