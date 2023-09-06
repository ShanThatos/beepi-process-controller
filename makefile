
.DEFAULT_GOAL := start
.ONE_SHELL:

start:
	poetry install
	poetry run python main.py

tailwind:
	npx tailwindcss -i ./static/tailwind-input.css -o ./static/tailwind-output.css --watch
