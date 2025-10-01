virtual:
	python -m venv venv

virtual_up:
	source ./venv/bin/activate

virtual_down:
	deactivate

freeze:
	pip freeze > requirements.txt

install:
	pip install -r requirements.txt
load:
	python -m venv venv
	source venv/bin/activate
	pip install -r requirements.txt

