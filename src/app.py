from flask import Flask, render_template, jsonify, request
import json
import logging
import os
from chrome_manager import ChromeManager
from order_extractor import OrderExtractor

app = Flask(__name__)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load config
def load_config():
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("Config file not found")
        return {}

chrome_manager = ChromeManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Check Chrome and tabs status"""
    config = load_config()
    status = chrome_manager.check_status(config)
    return jsonify(status)

@app.route('/api/launch-chrome', methods=['POST'])
def launch_chrome():
    """Launch Chrome with configured tabs"""
    config = load_config()
    result = chrome_manager.launch_chrome(config)
    return jsonify(result)

@app.route('/api/extract-order', methods=['POST'])
def extract_order():
    """Extract order data from BaseLinker and B2B Hendi"""
    try:
        logger.info("Extract order endpoint called")
        config = load_config()
        port = config.get('chrome_debug_port', 9222)
        
        logger.info(f"Creating OrderExtractor with port {port}")
        extractor = OrderExtractor(chrome_debug_port=port)
        
        logger.info("Calling extract_all_order_data()")
        order_data = extractor.extract_all_order_data()
        
        logger.info(f"Extraction complete, success={order_data.get('success')}")
        extractor.close()
        
        return jsonify(order_data)
    except Exception as e:
        logger.error(f"Error extracting order: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    config = load_config()
    return jsonify(config)

@app.route('/api/config', methods=['POST'])
def save_config():
    """Save configuration"""
    try:
        new_config = request.json
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(new_config, f, indent=2, ensure_ascii=False)
        logger.info("Configuration saved")
        return jsonify({"success": True, "message": "Configuration saved"})
    except Exception as e:
        logger.error(f"Failed to save config: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)