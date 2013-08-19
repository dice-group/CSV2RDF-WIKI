#!/bin/bash

echo "Getting the path of git repository (script file path)."
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
echo $DIR

echo "Removing link: /etc/supervisor/conf.d/csv2rdf-supervisor.conf"
sudo rm /etc/supervisor/conf.d/csv2rdf-supervisor.conf

echo "Removing link: /etc/nginx/sites-enabled/csv2rdf-nginx.conf" 
sudo rm /etc/nginx/sites-enabled/csv2rdf-nginx.conf 

echo "Removing entry from /etc/hosts file..."
sudo sed -i "/# __CSV2RDF__ begin/,/# __CSV2RDF__ end/d" /etc/hosts 

while true; do
    read -p "Delete local configuration files? [yn] " yn
    case $yn in
        [Yy]* ) 
            rm $DIR/webserver_config/csv2rdf-nginx.conf;
            rm $DIR/webserver_config/csv2rdf-supervisor.conf;
            rm $DIR/webserver_config/csv2rdf-uwsgi.ini;
            rm $DIR/webserver_config/uwsgi_params;
            rm $DIR/csv2rdf/config/config.py
            rm $DIR/csv2rdf/server/static/templates/baseUrl.mustache  
            rm $DIR/csv2rdf/server/static/templates/ckaninstance.mustache
            rm $DIR/csv2rdf/server/static/templates/wikiBaseUrl.mustache
            rm $DIR/csv2rdf/server/static/templates/wikiNamespace.mustache
            break;;
        [Nn]* ) 
            exit;;
        * ) echo "Please answer yes or no.";;
    esac
done
