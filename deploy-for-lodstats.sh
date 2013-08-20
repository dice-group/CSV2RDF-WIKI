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

echo "The virtual enviroment should be activated (for example, \$workon csv2rdf)."
echo "Current virtual enviroment: $VIRTUAL_ENV"

echo "Installing necessary site-packages..."
pip install -r $DIR/stable-req.txt

echo "Creating necessary folders..."
mkdir $DIR/sparqlified
mkdir $DIR/files
mkdir $DIR/logs

echo "Configuring application config..."
if [ -f $DIR/csv2rdf/config/config.py ]
then
    echo "Error: csv2rdf/config/config.py already exists!"
else
    cp $DIR/csv2rdf/config/config.py-template $DIR/csv2rdf/config/config.py
    read -p "Specify hostname (e.g. csv2rdf.aksw.org): " HOSTNAME
    read -p "Specify CKAN URI (e.g. http://publicdata.eu): " CKAN_BASEURI
    read -p "Specify CKAN API key (e.g. 00000000-0000-0000-0000-000000000000): " CKAN_API_KEY
    read -p "Specify WIKI URI (e.g. http://wiki.publicdata.eu): " WIKI_BASEURI
    read -p "Specify WIKI username: " WIKI_USERNAME
    read -p "Specify WIKI password: " WIKI_PASSWORD
    read -p "Specify WIKI namespace (e.g. Csv2rdf:): " WIKI_CSV2RDF_NAMESPACE

    sed -i "s%__HOSTNAME__%$HOSTNAME%g" $DIR/csv2rdf/config/config.py
    sed -i "s%__CKAN_BASEURI__%$CKAN_BASEURI%g" $DIR/csv2rdf/config/config.py
    sed -i "s%__CKAN_API_KEY__%$CKAN_API_KEY%g" $DIR/csv2rdf/config/config.py
    sed -i "s%__WIKI_BASEURI__%$WIKI_BASEURI%g" $DIR/csv2rdf/config/config.py
    sed -i "s%__WIKI_USERNAME__%$WIKI_USERNAME%g" $DIR/csv2rdf/config/config.py
    sed -i "s%__WIKI_PASSWORD__%$WIKI_PASSWORD%g" $DIR/csv2rdf/config/config.py
    sed -i "s%__WIKI_CSV2RDF_NAMESPACE__%$WIKI_CSV2RDF_NAMESPACE%g" $DIR/csv2rdf/config/config.py
    sed -i "s%__CSV2RDF__%$DIR%g" $DIR/csv2rdf/config/config.py
fi
