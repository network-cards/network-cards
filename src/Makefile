test :
	PYTHONPATH=. pytest tests.py

test-cov :
	PYTHONPATH=. pytest --cov=network_cards tests.py

latex-clean:
	latexmk -CA *.tex

latex-build:
	latexmk -gg main*.tex
