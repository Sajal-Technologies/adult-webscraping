from datetime import datetime, timedelta
import re
import subprocess

def naughty_convert_relative_time(relative_time):
    # Define regular expression pattern to extract numerical value and time unit
    pattern = r'(\d+)\s+(\w+)'

    # Match the pattern in the relative_time string
    match = re.match(pattern, relative_time)

    if match:
        # Extract numerical value and time unit
        value = int(match.group(1))
        unit = match.group(2).lower()

        # Map time units to timedelta arguments
        unit_mapping = {
            'year': 'years',
            'month': 'months',
            'week': 'weeks',
            'day': 'days'
        }

        # Calculate the date based on the provided relative time
        date = datetime.now() - timedelta(**{unit_mapping.get(unit, 'days'): value})

        # Format the date as "Sep 1, 2023"
        formatted_date = date.strftime("%b %d, %Y")

        return formatted_date

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr
def get_chrome_version():
    command = "google-chrome --version"
    stdout, stderr = run_command(command)

    return int(stdout.strip().split(' ')[-1].split('.')[0])
    

