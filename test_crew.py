import os
import urllib3
import warnings
import ssl
import logging

# Disable only CrewAI telemetry
os.environ["CREWAI_TELEMETRY"] = "false"

# Import after environment settings
from crews.crew import PostScreenshotCrew
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Suppress InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)
urllib3.disable_warnings(InsecureRequestWarning)

# Suppress SSL-related logs from OpenTelemetry
logging.getLogger('opentelemetry.sdk.trace.export').setLevel(logging.CRITICAL)
logging.getLogger('urllib3.connectionpool').setLevel(logging.CRITICAL)

# Create a custom SSL context that doesn't verify certificates
ssl._create_default_https_context = ssl._create_unverified_context

screenshot_url = "/Users/shakthiraveen/Downloads/SS Library/screenshots_notes/screenshot_2025-03-04_20-43-04.txt"
note = "Wow this is a nice wallpaper."

input_data = {
    "screenshot_url": screenshot_url,
    "note": note,
    "notes": note,
    "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

def run():
    crew_instance = PostScreenshotCrew()
    crew = crew_instance.crew()
    result = crew.kickoff(inputs=input_data)
    print(result)

if __name__ == "__main__":
    run()
