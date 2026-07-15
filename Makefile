.PHONY: test
test: .test.results

.test.results: $(wildcard *.py) $(wildcard */*.py) | .venv
	source .venv/bin/activate && python3 -m pytest tests/ | tee $@

.venv:
	uv venv .venv
	source .venv/bin/activate && uv pip install -r requirements.txt
