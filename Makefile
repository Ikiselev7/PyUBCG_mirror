.DEFAULT_GOAL := help

VENV_NAME=.venv
VENV_ACTIVATE=. $(VENV_NAME)/bin/activate
PYTHON=${VENV_NAME}/bin/python3.6


help:           ## Show available options with this Makefile
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'


.PHONY: clean_venv
clean_venv:     ## Clean the venv.
clean_venv:
	@rm -rf .Python MANIFEST build dist *venv* *.egg-info *.egg* ${VENV_NAME}
	@find . -type f -name "*.py[co]" -exec rm -rv {} +
	@find . -type d -name "__pycache__" -exec rm -rv {} +
	#@find . -type d -name "*.eggs" -exec rm -rv {} +



#.PHONY : test
#test:           ## Run all the tests
#test:
#	${PYTHON} setup.py test


venv: $(VENV_NAME)/bin/activate
$(VENV_NAME)/bin/activate: setup.py
	test -d $(VENV_NAME) || virtualenv -p python3.6 $(VENV_NAME)
	${PYTHON} -m pip install -U pip
	${PYTHON} -m pip install -e .
	touch $(VENV_NAME)/bin/activate


.PHONY: install_dep
install_dep:    ## Setup venv and install the application.
install_dep:
	mkdir logs || echo 'Folder already exist'
	make venv
	printf "#!/usr/bin/env bash\nsource $(VENV_NAME)/bin/activate" > venv.sh
	chmod +x venv.sh
