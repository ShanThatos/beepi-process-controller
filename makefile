
setup:
	python -m pip install -r requirements.txt
run:
	python main.py

push:
	git add .
	git commit -m "qpush-update"
	git push
