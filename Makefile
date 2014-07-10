backup:
	tar -cvzf data.tar.gz data files sparqlified sparqlified_exposed
backup_csv_only:
	tar -cvzf data.csv.tgz data files
deploy:
	python deploy.py
