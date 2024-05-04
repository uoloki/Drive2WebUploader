"""
Utilizing subprocess module to run scripts as if they were run from CLI
"""
import subprocess
import logging

# Set up logging
logging.basicConfig(filename='email_subprocess.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def run_script(script_name):
    """Run a Python script using subprocess and log output."""
    try:
        # Execute the script
        result = subprocess.run(['python', script_name], check=True, text=True, capture_output=True)
        if result.stdout:
            logging.info(f"Output from {script_name}:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error in {script_name}:\n{e.stderr}")

if __name__ == "__main__":
    # List of scripts to run
    scripts = ['drive_dw.py', 'selenium_upload.py', 'logs_email.py']

    # Execute each script in the list
    for script in scripts:
        run_script(script)
