import os
from dotenv import load_dotenv

# Automatically load backend/.env for all pytest test suites
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
