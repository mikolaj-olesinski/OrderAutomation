import subprocess
import platform
import requests
import logging
import os
import time

logger = logging.getLogger(__name__)

class ChromeManager:
    def __init__(self):
        self.system = platform.system()
        self._chrome_host = None
    
    def _get_chrome_host(self, port=9222):
        """Get the correct host for Chrome debugging"""
        # Cache the working host
        if self._chrome_host:
            return self._chrome_host
        
        # Try different hosts in order
        hosts = ['127.0.0.1']
        
        # Add Windows host IP if available (for Docker on Windows)
        windows_host_ip = os.environ.get('WINDOWS_HOST_IP')
        if windows_host_ip:
            hosts.insert(0, windows_host_ip)
        
        # Add host.docker.internal for Docker
        hosts.append('host.docker.internal')
        
        for host in hosts:
            try:
                response = requests.get(f'http://{host}:{port}/json', timeout=2)
                if response.status_code == 200:
                    self._chrome_host = host
                    logger.info(f"Chrome debug host detected: {host}")
                    return host
            except:
                continue
        
        # Default to localhost
        logger.warning(f"Could not find Chrome debug port on any host, defaulting to 127.0.0.1")
        return '127.0.0.1'
    
    def check_chrome_running(self, port=9222):
        """Check if Chrome is running with remote debugging"""
        try:
            host = self._get_chrome_host(port)
            response = requests.get(f'http://{host}:{port}/json', timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def get_open_tabs(self, port=9222):
        """Get list of open Chrome tabs"""
        try:
            host = self._get_chrome_host(port)
            response = requests.get(f'http://{host}:{port}/json', timeout=2)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            logger.error(f"Failed to get tabs: {e}")
            return []
    
    def find_tabs(self, config):
        """Find BaseLinker and B2B Hendi tabs"""
        tabs = self.get_open_tabs(config.get('chrome_debug_port', 9222))
        
        baselinker_tab = None
        b2b_hendi_tab = None
        
        baselinker_keywords = config.get('baselinker_keywords', ['baselinker', 'base', 'linker'])
        b2b_keywords = config.get('b2b_keywords', ['b2b', 'hendi'])
        
        for tab in tabs:
            title = tab.get('title', '').lower()
            url = tab.get('url', '').lower()
            
            # Check for BaseLinker
            if any(keyword in title or keyword in url for keyword in baselinker_keywords):
                baselinker_tab = tab
            
            # Check for B2B Hendi
            if any(keyword in title or keyword in url for keyword in b2b_keywords):
                b2b_hendi_tab = tab
        
        return baselinker_tab, b2b_hendi_tab
    
    def check_status(self, config):
        """Check overall status"""
        port = config.get('chrome_debug_port', 9222)
        chrome_running = self.check_chrome_running(port)
        
        status = {
            'chrome_running': chrome_running,
            'baselinker_open': False,
            'b2b_hendi_open': False,
            'system': self.system
        }
        
        if chrome_running:
            baselinker_tab, b2b_hendi_tab = self.find_tabs(config)
            status['baselinker_open'] = baselinker_tab is not None
            status['b2b_hendi_open'] = b2b_hendi_tab is not None
            
            if baselinker_tab:
                status['baselinker_title'] = baselinker_tab.get('title', 'Unknown')
            if b2b_hendi_tab:
                status['b2b_hendi_title'] = b2b_hendi_tab.get('title', 'Unknown')
        
        return status
    
    def get_chrome_path(self, config):
        """Get Chrome executable path based on OS"""
        custom_path = config.get('chrome_path')
        if custom_path and os.path.exists(custom_path):
            return custom_path
        
        if self.system == 'Windows':
            default_paths = [
                r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
            ]
        elif self.system == 'Darwin':  # macOS
            default_paths = [
                '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            ]
        else:  # Linux
            default_paths = [
                '/usr/bin/google-chrome',
                '/usr/bin/chromium-browser',
            ]
        
        for path in default_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def launch_chrome(self, config):
        """Launch Chrome with remote debugging and open tabs via helper service"""
        try:
            # Try to use helper service (for Docker or when helper is running)
            helper_url = config.get('helper_service_url', 'http://127.0.0.1:5001')
            
            # Check if we're in Docker
            in_docker = os.environ.get('IN_DOCKER', 'false').lower() == 'true'
            
            if in_docker:
                # In Docker, we must use helper service on host
                helper_url = 'http://host.docker.internal:5001'
            
            try:
                # Try to reach helper service
                health_check = requests.get(f'{helper_url}/health', timeout=2)
                
                if health_check.status_code == 200:
                    # Helper service is available, use it
                    logger.info(f"Using Chrome Launcher Helper at {helper_url}")
                    
                    response = requests.post(
                        f'{helper_url}/launch-chrome',
                        json=config,
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        return response.json()
                    else:
                        result = response.json()
                        return {
                            'success': False,
                            'error': result.get('error', 'Unknown error from helper service')
                        }
                        
            except requests.exceptions.RequestException as e:
                logger.warning(f"Helper service not available: {e}")
                
                if in_docker:
                    # In Docker and no helper service - can't launch Chrome
                    return {
                        'success': False,
                        'error': 'Chrome Launcher Helper service not running. Please start it on your host machine.'
                    }
            
            # Not in Docker and helper not available - try direct launch
            logger.info("Attempting direct Chrome launch...")
            
            chrome_path = self.get_chrome_path(config)
            if not chrome_path:
                return {
                    'success': False,
                    'error': 'Chrome executable not found'
                }
            
            port = config.get('chrome_debug_port', 9222)
            user_data_dir = config.get('chrome_user_data_dir', '')
            baselinker_url = config.get('baselinker_url', '')
            b2b_hendi_url = config.get('b2b_hendi_url', '')
            
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
            if self.system == 'Windows':
                subprocess.Popen(cmd, shell=True)
            else:
                subprocess.Popen(cmd)
            
            # Wait a bit for Chrome to start
            time.sleep(2)
            
            return {
                'success': True,
                'message': 'Chrome launched successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to launch Chrome: {e}")
            return {
                'success': False,
                'error': str(e)
            }