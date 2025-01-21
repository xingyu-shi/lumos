import os

# WORKING_DIR = "workspace2"
WORKING_DIR = "workspace_gpt4o_mini"
if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)

BASEDIR = os.path.abspath(os.path.dirname(__file__))


CHUNK_TOKEN_SIZE = 1200