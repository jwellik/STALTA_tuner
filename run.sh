#! /bin/bash

bokeh serve --show . --websocket-max-message-size 52428800 --args $1
