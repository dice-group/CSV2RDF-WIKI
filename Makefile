backup:
	tar -cvzf data.tar.gz data files sparqlified sparqlified_exposed
deploy:
	python deploy.py
