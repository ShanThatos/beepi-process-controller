
.DEFAULT_GOAL := start
.ONE_SHELL:

start:
	poetry install
	poetry run python main.py

push:
	pip freeze > requirements.txt
	git add .
	git commit -m "make-push-update"
	git push

tailwind:
	npx tailwindcss -i ./static/tailwind-input.css -o ./static/tailwind-output.css --watch

restart:
	$(MAKE) run