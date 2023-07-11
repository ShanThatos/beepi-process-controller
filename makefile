
.DEFAULT_GOAL := all

all: setup run

setup:
	pip install -r requirements.txt
run:
	python main.py

push:
	pip freeze > requirements.txt
	git add .
	git commit -m "make-push-update"
	git push
