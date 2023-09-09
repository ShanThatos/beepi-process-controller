
.DEFAULT_GOAL := all
.ONE_SHELL:

all: setup start

setup:
	poetry install

start:
	poetry run python main.py

tailwind:
	npx tailwindcss -i ./static/tailwind-input.css -o ./static/tailwind-output.css --watch
