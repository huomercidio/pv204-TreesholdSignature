import os
import subprocess
import logging
from typing import List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('signer_manager.log'),
        logging.StreamHandler()
    ]
)


class SignerManager:
    @staticmethod
    def find_env_files() -> List[str]:
        return sorted(
            [f for f in os.listdir('.')
             if f.startswith('.env.share') and f[len('.env.share'):].isdigit()],
            key=lambda x: int(x.split('.env.share')[1]))

    def run(self) -> None:
        env_files = self.find_env_files()
        if not env_files:
            logging.error("No valid .env.share files found")
            return

        logging.info(f"Starting {len(env_files)} signers...")

        try:
            # Start all signers (they'll manage their own lifecycle)
            for env_file in env_files:
                subprocess.Popen(
                    ["python", "auto_signer.py", "--env", env_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8'
                )
                logging.info(f"Started signer from {env_file}")

        except Exception as e:
            logging.error(f"Failed to start signers: {str(e)}")


if __name__ == "__main__":
    SignerManager().run()
