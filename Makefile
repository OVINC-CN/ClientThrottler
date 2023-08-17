init_build:
	pip install setuptools wheel twine build
build:
	python -m build # generating a source-distribution and wheel
check:
	twine check dist/*
publish: build check
	twine upload dist/*
clean:
	rm -r client_throttler.egg-info dist
dev:
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements_dev.txt
