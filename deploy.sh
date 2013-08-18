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
    read -p "Specify the hostname (for instance, www.example.com): " HOSTNAME
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
