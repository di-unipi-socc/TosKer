#!/bin/sh
coverage run --source tosker -m unittest discover
coverage report -m
coverage html
