import re
from datetime import datetime
import requests
from flask import Flask, jsonify

app = Flask(__name__)

# Simulated log file path
LOG_FILE = "/var/log/app/error.log"

def parse_logs(log_file, error_pattern=r'ERROR:\s+(.*)'):
    """Parse logs for critical errors and trigger alerts."""
    errors = []
    with open(log_file, 'r') as f:
        for line in f:
            match = re.search(error_pattern, line)
            if match:
                errors.append({
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'message': match.group(1).strip(),
                    'severity': 'CRITICAL'
                })
    
    # Send alerts to monitoring tools
    if errors:
        send_to_splunk(errors)
        send_to_teams_webhook(errors)
    
    return errors

def send_to_splunk(errors):
    """Send parsed errors to Splunk HTTP Event Collector."""
    headers = {'Authorization': 'Splunk token_name'}
    for error in errors:
        requests.post(
            url='https://splunk-server:8088/services/collector',
            json=error,
            headers=headers
        )

def send_to_teams_webhook(errors):
    """Post alerts to Microsoft Teams channel."""
    teams_payload = {
        "text": f"{len(errors)} critical errors detected!",
        "sections": [{"facts": [{"name": e['message'], "value": e['timestamp']} for e in errors]}]
    }
    requests.post(
        url='https://webhook.office.com/Teams_Cloud_Webhook',
        json=teams_payload
    )

@app.route('/health')
def health_check():
    return jsonify({"status": "OK", "version": "1.0.0"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
