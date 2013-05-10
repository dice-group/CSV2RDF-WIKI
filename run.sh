#!/bin/sh

until nohup python run.py; do
    echo "Server 'csv2rdf server' crashed with exit code $?.  Respawning.." >&2
    sleep 1
done
