
.DEFAULT_GOAL := all
.ONE_SHELL:

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

tailwind:
	npx tailwindcss -i ./static/tailwind-input.css -o ./static/tailwind-output.css --watch

restart:
	$(MAKE) run