import os
import subprocess
import time
from dotenv import dotenv_values

SIGNER_SCRIPT = "auto_signer.py"
env_files = [".env.1", ".env.2", ".env.3"]

print("🚀 Starting multi-device auto signer simulation...\n")

for env_file in env_files:
    env_values = dotenv_values(env_file)
    share_id = env_values.get("SHARE_ID", "unknown")
    print("🔁 Running signer for SHARE_ID={}".format(share_id))

    env = os.environ.copy()
    env.update(env_values)  #
    subprocess.call(["python", SIGNER_SCRIPT], env=env)

    print("-" * 40)
    time.sleep(1)
