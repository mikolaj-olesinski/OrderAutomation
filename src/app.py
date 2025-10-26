from flask import Flask, render_template, jsonify, request
import json
import logging
import os
import sys
from chrome_manager import ChromeManager
from extractors import OrderCoordinator, B2BExtractor

app = Flask(__name__)

# Setup logging with UTF-8 encoding for Windows
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Fix console encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

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

@app.route('/api/logs')
def get_logs():
    """Get recent logs from app.log file"""
    try:
        log_file = 'app.log'
        if not os.path.exists(log_file):
            return jsonify({'logs': []})
        
        # Read last 100 lines from log file
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Get last 100 lines
            recent_lines = lines[-100:] if len(lines) > 100 else lines
            
        return jsonify({'logs': recent_lines})
    except Exception as e:
        logger.error(f"Failed to read logs: {e}")
        return jsonify({'logs': [], 'error': str(e)})

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
        
        logger.info(f"Creating OrderCoordinator with port {port}")
        coordinator = OrderCoordinator(chrome_debug_port=port)
        
        logger.info("Calling extract_all_order_data()")
        order_data = coordinator.extract_all_order_data()
        
        logger.info(f"Extraction complete, success={order_data.get('success')}")
        
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

@app.route('/api/open-import-modal', methods=['POST'])
def open_import_modal():
    """Open the import products modal on B2B Hendi"""
    try:
        logger.info("Open import modal endpoint called")
        config = load_config()
        port = config.get('chrome_debug_port', 9222)
        
        extractor = B2BExtractor(chrome_debug_port=port)
        
        # Connect to Chrome
        if not extractor.connect_to_chrome():
            return jsonify({
                "success": False,
                "error": "Could not connect to Chrome"
            }), 500
        
        # Switch to B2B Hendi tab
        if not extractor.find_b2b_hendi_tab():
            extractor.close()
            return jsonify({
                "success": False,
                "error": "B2B Hendi tab not found"
            }), 404
        
        # Click the import button
        result = extractor.click_import_products_button()
        extractor.close()
        
        if result:
            return jsonify({
                "success": True,
                "message": "Import modal opened successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to open import modal"
            }), 500
            
    except Exception as e:
        logger.error(f"Error opening import modal: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/import-products', methods=['POST'])
def import_products():
    """Create CSV from products and import to B2B Hendi"""
    try:
        logger.info("Import products endpoint called")
        
        # Get products from request
        data = request.json
        products = data.get('products', [])
        
        if not products:
            return jsonify({
                "success": False,
                "error": "No products provided"
            }), 400
        
        config = load_config()
        port = config.get('chrome_debug_port', 9222)
        
        # Use OrderCoordinator for simplified import
        coordinator = OrderCoordinator(chrome_debug_port=port)
        result = coordinator.import_products_to_b2b(products)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error importing products: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/complete-order', methods=['POST'])
def complete_order():
    """Complete order: import products and fill delivery address"""
    try:
        logger.info("Complete order endpoint called")
        
        # Get data from request
        data = request.json
        products = data.get('products', [])
        address = data.get('address', {})
        payment_amount = data.get('payment_amount', None)
        
        if not products:
            return jsonify({
                "success": False,
                "error": "No products provided"
            }), 400
        
        if not address:
            return jsonify({
                "success": False,
                "error": "No address data provided"
            }), 400
        
        # Prepare address data for B2B format
        # Use full address in street field, dot in building number
        address_data = {
            'name': address.get('company', ''),
            'phone': address.get('phone', ''),
            'email': data.get('email', ''),
            'street': address.get('address', ''),  # Full address in street
            'street_no': '.',  # Dot as building number
            'street_flat': '',  # Optional
            'zip': address.get('postal_code', ''),
            'city': address.get('city', '')
        }
        
        config = load_config()
        port = config.get('chrome_debug_port', 9222)
        
        # Use OrderCoordinator for complete order
        coordinator = OrderCoordinator(chrome_debug_port=port)
        result = coordinator.complete_order_with_address(products, address_data, payment_amount)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error completing order: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)