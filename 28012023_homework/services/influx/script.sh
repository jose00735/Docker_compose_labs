#!/bin/bash
sleep 5
influx setup --org org --bucket bucket --username root --password Illbelookingforyou --force
#influx auth create --all-access --host http://influxdb:8086 --org org --token Illbelookingforyou

