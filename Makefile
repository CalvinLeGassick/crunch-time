build_db:
	createdb crunchy
	psql -d crunchy -a -f startup.sql

destroy_db:
	dropdb crunchy

reset_db: destroy_db build_db

company_names:
	psql -d crunchy -c "SELECT name FROM COMPANY;"

setup_config:
	mv .example_config.py config.py