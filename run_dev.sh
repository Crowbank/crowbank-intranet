#!/bin/bash

# Load configuration from dev.config
export $(grep -v '^#' dev.config | xargs)

# Run the application in debug mode
python run.py --debug 