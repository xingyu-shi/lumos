#!/bin/bash

# directory: lumos/bin
WORK_HOME=$(cd $(dirname $0); pwd)
cd "$WORK_HOME"

#python ../build_rag.py --source='/Users/xingyushi/code/personal/lumos/Crawler/olh_workspace_v2'
python ../build_rag.py --source='/Users/xingyushi/code/personal/lumos/Crawler/workspace_ems'