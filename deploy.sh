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
    read -p "Specify hostname [csv2rdf.aksw.org]: " HOSTNAME
    read -p "Specify CKAN URI [http://publicdata.eu]: " CKAN_BASEURI
    read -p "Specify CKAN API key [00000000-0000-0000-0000-000000000000]: " CKAN_API_KEY
    read -p "Specify WIKI URI [http://wiki.publicdata.eu]: " WIKI_BASEURI
    read -p "Specify WIKI username [wiki_username]: " WIKI_USERNAME
    read -p "Specify WIKI password [wiki_password]: " WIKI_PASSWORD
    read -p "Specify WIKI namespace [Csv2rdf:]: " WIKI_CSV2RDF_NAMESPACE
    read -p "Specify the number of Sparqlify (Java) workers [5]: " SPARQLIFY_JAVA_WORKERS

    #Defaults
    [ -z "$HOSTNAME" ] && HOSTNAME="csv2rdf.aksw.org"
    [ -z "$CKAN_BASEURI" ] && CKAN_BASEURI="http://publicdata.eu"
    [ -z "$CKAN_API_KEY" ] && CKAN_API_KEY="00000000-0000-0000-0000-000000000000"
    [ -z "$WIKI_BASEURI" ] && WIKI_BASEURI="http://wiki.publicdata.eu"
    [ -z "$WIKI_USERNAME" ] && WIKI_USERNAME="wiki_username"
    [ -z "$WIKI_PASSWORD" ] && WIKI_PASSWORD="wiki_password"
    [ -z "$WIKI_CSV2RDF_NAMESPACE" ] && WIKI_CSV2RDF_NAMESPACE="Csv2rdf:"
    [ -z "$SPARQLIFY_JAVA_WORKERS" ] && SPARQLIFY_JAVA_WORKERS="5"

    sed -i "s%__HOSTNAME__%$HOSTNAME%g" $DIR/csv2rdf/config/config.py
    sed -i "s%__CKAN_BASEURI__%$CKAN_BASEURI%g" $DIR/csv2rdf/config/config.py
    sed -i "s%__CKAN_API_KEY__%$CKAN_API_KEY%g" $DIR/csv2rdf/config/config.py
    sed -i "s%__WIKI_BASEURI__%$WIKI_BASEURI%g" $DIR/csv2rdf/config/config.py
    sed -i "s%__WIKI_USERNAME__%$WIKI_USERNAME%g" $DIR/csv2rdf/config/config.py
    sed -i "s%__WIKI_PASSWORD__%$WIKI_PASSWORD%g" $DIR/csv2rdf/config/config.py
    sed -i "s%__WIKI_CSV2RDF_NAMESPACE__%$WIKI_CSV2RDF_NAMESPACE%g" $DIR/csv2rdf/config/config.py
    sed -i "s%__CSV2RDF__%$DIR%g" $DIR/csv2rdf/config/config.py
fi

echo "Configuring mustache templates..."
if [ -f $DIR/csv2rdf/server/static/templates/baseUrl.mustache ]
then
    echo "Error: mustache templates already exist!"
else
    cp $DIR/csv2rdf/server/static/templates/baseUrl.mustache-template $DIR/csv2rdf/server/static/templates/baseUrl.mustache
    sed -i "s%__HOSTNAME__%$HOSTNAME%g" $DIR/csv2rdf/server/static/templates/baseUrl.mustache
    cp $DIR/csv2rdf/server/static/templates/ckaninstance.mustache-template $DIR/csv2rdf/server/static/templates/ckaninstance.mustache
    sed -i "s%__CKAN_BASEURI__%$CKAN_BASEURI%g" $DIR/csv2rdf/server/static/templates/ckaninstance.mustache
    cp $DIR/csv2rdf/server/static/templates/wikiBaseUrl.mustache-template $DIR/csv2rdf/server/static/templates/wikiBaseUrl.mustache
    sed -i "s%__WIKI_BASEURI__%$WIKI_BASEURI%g" $DIR/csv2rdf/server/static/templates/wikiBaseUrl.mustache
    cp $DIR/csv2rdf/server/static/templates/wikiNamespace.mustache-template $DIR/csv2rdf/server/static/templates/wikiNamespace.mustache
    sed -i "s%__WIKI_CSV2RDF_NAMESPACE__%$WIKI_CSV2RDF_NAMESPACE%g" $DIR/csv2rdf/server/static/templates/wikiNamespace.mustache
fi


echo "Configuring uwsgi..."
if [ -f $DIR/webserver_config/csv2rdf-uwsgi.ini ]
then
    echo "Error: will not deploy uwsgi. Configuration already exists!"
else
    cp $DIR/webserver_config/templates/csv2rdf-uwsgi.ini-template $DIR/webserver_config/csv2rdf-uwsgi.ini
    sed -i "s%__VIRTUAL_ENV__%$VIRTUAL_ENV%g" $DIR/webserver_config/csv2rdf-uwsgi.ini
    sed -i "s%__CSV2RDF__%$DIR%g" $DIR/webserver_config/csv2rdf-uwsgi.ini
fi

echo "Setting uwsgi parameters..."
if [ -f $DIR/webserver_config/uwsgi_params ]
then
    echo "Error: uwsgi_params file already exists!"
else
    cp $DIR/webserver_config/templates/uwsgi_params-template $DIR/webserver_config/uwsgi_params
fi

echo "Configuring supervisor..."
if [ -f $DIR/webserver_config/csv2rdf-supervisor.conf ]
then
    echo "Error: will not deploy supervisor. Configuration already exists!"
else
    cp $DIR/webserver_config/templates/csv2rdf-supervisor.conf-template $DIR/webserver_config/csv2rdf-supervisor.conf

    for((i=1; i<=$SPARQLIFY_JAVA_WORKERS; i++))
    do
        echo "" >> $DIR/webserver_config/csv2rdf-supervisor.conf
        sed "s%__ITERATOR__%$i%g" $DIR/webserver_config/templates/csv2rdf-supervisor-sparqlify_java_handler.conf-template >> $DIR/webserver_config/csv2rdf-supervisor.conf
    done

    sed -i "s%__VIRTUAL_ENV__%$VIRTUAL_ENV%g" $DIR/webserver_config/csv2rdf-supervisor.conf
    sed -i "s%__CSV2RDF__%$DIR%g" $DIR/webserver_config/csv2rdf-supervisor.conf

    echo "Linking created configuration to /etc/supervisor/conf.d/csv2rdf-supervisor.conf ..." 
    sudo ln -s $DIR/webserver_config/csv2rdf-supervisor.conf /etc/supervisor/conf.d/csv2rdf-supervisor.conf
    sudo service supervisor stop
    sudo service supervisor start
fi

echo "Configuring nginx..."
if [ -f $DIR/webserver_config/csv2rdf-nginx.conf ]
then
    echo "Error: will not deploy nginx. Configuration already exists!"
else
    cp $DIR/webserver_config/templates/csv2rdf-nginx.conf-template $DIR/webserver_config/csv2rdf-nginx.conf
    sed -i "s%__CSV2RDF__%$DIR%g" $DIR/webserver_config/csv2rdf-nginx.conf
    sed -i "s%__HOSTNAME__%$HOSTNAME%g" $DIR/webserver_config/csv2rdf-nginx.conf
    echo "Linking created configuration to /etc/nginx/sites-enabled/csv2rdf-nginx.conf ..."
    sudo ln -s $DIR/webserver_config/csv2rdf-nginx.conf /etc/nginx/sites-enabled/csv2rdf-nginx.conf

    while true; do
        read -p "Developer's deploy? (will edit /etc/hosts) [yn] " yn
        case $yn in
            [Yy]* ) 
                echo "# __CSV2RDF__ begin" | sudo tee -a /etc/hosts; 
                echo "127.0.0.1 $HOSTNAME" | sudo tee -a /etc/hosts; 
                echo "# __CSV2RDF__ end" | sudo tee -a /etc/hosts; 
                break;;
            [Nn]* ) 
                exit;;
            * ) echo "Please answer yes or no.";;
        esac
    done

    echo "Restarting nginx..."
    sudo service nginx restart
fi
