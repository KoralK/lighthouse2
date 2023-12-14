import requests
import json
import os
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
import time

logging.basicConfig(filename='lighthouse_data.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# rest of your imports and code follow here...

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set up the scheduler
scheduler = BlockingScheduler()

# Retrieve New Relic API key from environment variable
new_relic_insert_key = os.getenv('NEW_RELIC_API_KEY')
if not new_relic_insert_key:
    logging.error("No New Relic API key found. Set the NEW_RELIC_API_KEY environment variable.")
    raise ValueError("No New Relic API key found. Set the NEW_RELIC_API_KEY environment variable.")

# Your New Relic Account ID
new_relic_account_id = '4275397'

# Your Google PageSpeed API Key
google_api_key = os.getenv('GOOGLE_API_KEY')
if not google_api_key:
    logging.error("No Google API key found. Set the GOOGLE_API_KEY environment variable.")
    raise ValueError("No Google API key found. Set the GOOGLE_API_KEY environment variable.")

# The URL you want to check
url_to_check = 'https://au.pandora.net/en'

def fetch_lighthouse_data():
    logging.info(f"Fetching Lighthouse data for {url_to_check}")
    try:
        # Call the Google PageSpeed Insights API
        api_url = f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url_to_check}&key={google_api_key}'
        response = requests.get(api_url)
        response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code
        data = response.json()

        # Extract the necessary metrics from the response
        metrics = {
            'firstContentfulPaint': data['lighthouseResult']['audits']['first-contentful-paint']['numericValue'],
            'largestContentfulPaint': data['lighthouseResult']['audits']['largest-contentful-paint']['numericValue'],
            # Add other metrics as necessary
        }

        # Format data for New Relic
        new_relic_data = {
            'eventType': 'LighthouseMetrics',
            'url': url_to_check,
            **metrics
        }

        # Send data to New Relic
        headers = {
            'Api-Key': new_relic_insert_key,
            'Content-Type': 'application/json'
        }
        nr_url =f'https://insights-collector.eu01.nr-data.net/v1/accounts/{new_relic_account_id}/events'
        nr_response = requests.post(nr_url, headers=headers, data=json.dumps([new_relic_data]))
        nr_response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code

        logging.info(f"Data posted to New Relic successfully for {url_to_check}")
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
    except Exception as err:
        logging.error(f"An error occurred: {err}")

# Schedule the function to run every hour
# Schedule the function to run every 2 minutes
scheduler.add_job(fetch_lighthouse_data, 'interval', minutes=1)
#scheduler.add_job(fetch_lighthouse_data, 'interval', hours=1)

# At the end of your script, instead of starting the scheduler, run the function directly
# Comment out the scheduler.start() line and add:
#if __name__ == "__main__":
#    fetch_lighthouse_data()

# Start the scheduler

if __name__ == "__main__":
    for _ in range(2):  # Run it 2 times
        fetch_lighthouse_data()
        time.sleep(120)  # Wait for 2 minutes before the next run

#try:
#    scheduler.start()
#except (KeyboardInterrupt, SystemExit):
#    pass
