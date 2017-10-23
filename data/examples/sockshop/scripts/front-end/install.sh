#!/bin/sh

git clone -b $INPUT_BRANCH $INPUT_REPO /front-end
cd /front-end
npm install
