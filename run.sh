#! /bin/bash

bokeh serve --show ./main.py --websocket-max-message-size 52428800 --args $1
