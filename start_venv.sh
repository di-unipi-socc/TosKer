#!/bin/sh
if [ ! -d "venv" ]; then
  virtualenv venv
fi

. ./venv/bin/activate
