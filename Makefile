#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = ec1
PYTHON_VERSION = 3.11
PYTHON_INTERPRETER = python

#################################################################################
# VARIABLES                                                                	#
#################################################################################

PYTHON = python

SCRIPT_VALIDATE     = src\validar.py
SCRIPT_IMPUTE       = src\imputar.py
SCRIPT_TRANSFORM    = src\transformar.py
SCRIPT_SUMMARIZE    = src\resumir.py
SCRIPT_REPORT       = src\reporte.py

RAW_DATA            = data\raw\estudiantes.csv
VALIDATED_CSV       = data\interim\validado.csv
VALIDATION_TXT      = data\interim\reporte_validacion.txt
IMPUTED_CSV         = data\interim\imputado.csv
TRANSFORMED_CSV     = data\processed\transformado.csv
SUMMARY_TXT         = data\processed\resumen.txt
FINAL_REPORT     	= reports\reporte_final.md

#################################################################################
# Default Target                                                                #
#################################################################################

.DEFAULT_GOAL := all

#################################################################################
# COMMANDS                                                                      #
#################################################################################

.PHONY: all
all: lint $(FINAL_REPORT)

#################################################################################
# CODE QUALITY                                                           		#
#################################################################################

.PHONY: lint
lint:
	ruff format --check
	ruff check

.PHONY: format
format:
	ruff check --fix
	ruff format

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################

#################################################################################
# PIPELINE                                                           			#
#################################################################################

$(VALIDATED_CSV) $(VALIDATION_TXT): $(RAW_DATA)	$(SCRIPT_VALIDATE)
	$(PYTHON) $(SCRIPT_VALIDATE)

$(IMPUTED_CSV): $(VALIDATED_CSV) $(SCRIPT_IMPUTE)
	$(PYTHON) $(SCRIPT_IMPUTE)

$(TRANSFORMED_CSV): $(IMPUTED_CSV) $(SCRIPT_TRANSFORM)
	$(PYTHON) $(SCRIPT_TRANSFORM)

$(SUMMARY_TXT): $(TRANSFORMED_CSV) $(SCRIPT_SUMMARIZE)
	$(PYTHON) $(SCRIPT_SUMMARIZE)

$(FINAL_REPORT): $(TRANSFORMED_CSV) $(SUMMARY_TXT) $(SCRIPT_REPORT)
	$(PYTHON) $(SCRIPT_REPORT)


################################################################################
# MAINTENANCE                                                                  #
################################################################################

.PHONY: clean
clean:
	-@if exist $(VALIDATED_CSV) del /f /q $(VALIDATED_CSV)
	-@if exist $(VALIDATION_TXT) del /f /q $(VALIDATION_TXT)
	-@if exist $(IMPUTED_CSV) del /f /q $(IMPUTED_CSV)
	-@if exist $(TRANSFORMED_CSV) del /f /q $(TRANSFORMED_CSV)
	-@if exist $(SUMMARY_TXT) del /f /q $(SUMMARY_TXT)
	-@if exist $(FINAL_REPORT) del /f /q $(FINAL_REPORT)

	-@del /s /q *.pyc >nul 2>&1
	-@del /s /q *.pyo >nul 2>&1
	-@for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" >nul 2>&1

	@echo "Archivos borrados con exito!"

.PHONY: status
status:
	@echo  ------ ESTADO DE PIPELINE ------
	@if exist $(RAW_DATA) (echo [OK] $(RAW_DATA)) else (echo [Faltante] $(RAW_DATA))
	@if exist $(VALIDATED_CSV) (echo [OK] $(VALIDATED_CSV)) else (echo [Faltante] $(VALIDATED_CSV))
	@if exist $(VALIDATION_TXT) (echo [OK] $(VALIDATION_TXT)) else (echo [Faltante] $(VALIDATION_TXT))
	@if exist $(IMPUTED_CSV) (echo [OK] $(IMPUTED_CSV)) else (echo [Faltante] $(IMPUTED_CSV))
	@if exist $(TRANSFORMED_CSV) (echo [OK] $(TRANSFORMED_CSV)) else (echo [Faltante] $(TRANSFORMED_CSV))
	@if exist $(SUMMARY_TXT) (echo [OK] $(SUMMARY_TXT)) else (echo [Faltante] $(SUMMARY_TXT))
	@if exist $(FINAL_REPORT) (echo [OK] $(FINAL_REPORT)) else (echo [Faltante] $(FINAL_REPORT))

#################################################################################
# Environment                                                          			#
#################################################################################

## Set up Python interpreter environment
.PHONY: create_environment
create_environment:
	conda env create --name $(PROJECT_NAME) -f environment.yml
	
	@echo ">>> conda env created. Activate with:\nconda activate $(PROJECT_NAME)"

## Install Python dependencies
.PHONY: requirements
requirements:
	conda env update --name $(PROJECT_NAME) --file environment.yml --prune

#################################################################################
# Self Documenting Commands                                                     #
#################################################################################


define PRINT_HELP_PYSCRIPT
import re, sys; \
lines = '\n'.join([line for line in sys.stdin]); \
matches = re.findall(r'\n## (.*)\n[\s\S]+?\n([a-zA-Z_-]+):', lines); \
print('Available rules:\n'); \
print('\n'.join(['{:25}{}'.format(*reversed(match)) for match in matches]))
endef
export PRINT_HELP_PYSCRIPT

help:
	@$(PYTHON_INTERPRETER) -c "${PRINT_HELP_PYSCRIPT}" < $(MAKEFILE_LIST)
