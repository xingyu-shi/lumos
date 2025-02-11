#!/bin/bash

WORK_HOME=$(cd $(dirname $0); pwd)
cd "$WORK_HOME/../"

fastapi run "$WORK_HOME/../lumos/main.py"