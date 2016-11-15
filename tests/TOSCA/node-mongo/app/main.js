/* jslint node: true */
"use strict";
var express = require('express');
var mongoose = require('mongoose');

function connect_to_mongo() {
    // console.log('try to connect...');
    mongoose.connect('mongodb://db/data1', function(err) {
        if (err) {
            // console.log('error: ' + err.message);
            connect_to_mongo();
        } else
            console.log('connection successful');
    });
}
connect_to_mongo();

var Schema = mongoose.Schema;
var PeopleSchema = mongoose.model('People',
    new Schema({
        name: String,
        surname: String
    })
);
new PeopleSchema({
    name: 'Mario',
    surname: 'Rossi'
}).save();
new PeopleSchema({
    name: 'Mario',
    surname: 'Verdi'
}).save();

var app = express();
app.get('/hello', function(req, res) {
    res.send('hello-world');
});

app.get('/', function(req, res) {
    PeopleSchema.find(function(err, people) {
        res.send(people);
    });
});

app.listen(process.env.PORT || 80, function() {
    console.log('server listen on port ' + (process.env.PORT || 80));
});
