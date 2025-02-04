.PHONY: setup run clean

# Detect OS
ifeq ($(OS),Windows_NT)
    PYTHON = python
    VENV_BIN = .venv\Scripts
    ACTIVATE = $(VENV_BIN)\activate.bat
    RM = rmdir /s /q
else
    PYTHON = python3
    VENV_BIN = .venv/bin
    ACTIVATE = . $(VENV_BIN)/activate
    RM = rm -rf
endif

# Default target
all: setup run

# Setup virtual environment and install dependencies
setup:
	@echo "Setting up virtual environment..."
	$(PYTHON) -m venv .venv
	@echo "Installing dependencies..."
ifeq ($(OS),Windows_NT)
	call $(ACTIVATE) && pip install -r requirements.txt
else
	$(ACTIVATE) && pip install -r requirements.txt
endif

# Run the application
run:
ifeq ($(OS),Windows_NT)
	call $(ACTIVATE) && $(PYTHON) main.py
else
	$(ACTIVATE) && $(PYTHON) main.py
endif

# Clean up virtual environment
clean:
	$(RM) .venv
	@echo "Cleaned up virtual environment"

# Install and run in one command
install-and-run: setup run 