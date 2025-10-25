"""
Chrome Launcher Helper Service
Runs on the host machine (not in Docker) and launches Chrome when requested
"""
from flask import Flask, request, jsonify
import subprocess
import platform
import os
import logging

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_chrome_path():
    """Get Chrome executable path based on OS"""
    system = platform.system()
    
    if system == 'Windows':
        paths = [
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
            os.path.expanduser(r'~\AppData\Local\Google\Chrome\Application\chrome.exe'),
        ]
    elif system == 'Darwin':  # macOS
        paths = [
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        ]
    else:  # Linux
        paths = [
            '/usr/bin/google-chrome',
            '/usr/bin/chromium-browser',
        ]
    
    for path in paths:
        if os.path.exists(path):
            return path
    
    return None

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'system': platform.system()})

@app.route('/launch-chrome', methods=['POST'])
def launch_chrome():
    """Launch Chrome with provided configuration"""
    try:
        data = request.json
        
        chrome_path = data.get('chrome_path')
        if not chrome_path:
            chrome_path = get_chrome_path()
        
        if not chrome_path:
            return jsonify({
                'success': False,
                'error': 'Chrome executable not found'
            }), 404
        
        port = data.get('chrome_debug_port', 9222)
        user_data_dir = data.get('chrome_user_data_dir', '')
        baselinker_url = data.get('baselinker_url', '')
        b2b_hendi_url = data.get('b2b_hendi_url', '')
        
        # Build command
        cmd = [
            chrome_path,
            f'--remote-debugging-port={port}',
            '--remote-debugging-address=0.0.0.0'  # Allow access from Docker
        ]
        
        if user_data_dir:
            cmd.append(f'--user-data-dir={user_data_dir}')
        
        if baselinker_url:
            cmd.append(baselinker_url)
        
        if b2b_hendi_url:
            cmd.append(b2b_hendi_url)
        
        logger.info(f"Launching Chrome: {' '.join(cmd)}")
        
        # Launch Chrome
        if platform.system() == 'Windows':
            subprocess.Popen(cmd, shell=True)
        else:
            subprocess.Popen(cmd)
        
        return jsonify({
            'success': True,
            'message': 'Chrome launched successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to launch Chrome: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    system = platform.system()
    logger.info(f"Chrome Launcher Helper starting on {system}...")
    logger.info("This service must run on the HOST machine (not in Docker)")
    logger.info("Listening on http://0.0.0.0:5001 (accessible from Docker)")
    app.run(host='0.0.0.0', port=5001, debug=False)