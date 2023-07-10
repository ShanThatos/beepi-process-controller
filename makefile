
.DEFAULT_GOAL := all

all: setup run

setup:
	git pull
	python -m pip install -r requirements.txt
run:
	python main.py

push:
	git add .
	git commit -m "make-push-update"
	git push
