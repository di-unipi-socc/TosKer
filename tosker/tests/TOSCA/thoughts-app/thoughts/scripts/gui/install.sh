#!/bin/sh

git clone -b $INPUT_BRANCH $INPUT_REPO thoughts-gui

cd thoughts-gui
npm install
