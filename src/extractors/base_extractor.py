"""
Base Extractor
Common Selenium logic for all extractors
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import logging
import os
import stat

logger = logging.getLogger(__name__)

class BaseExtractor:
    """Base class for all extractors with common Selenium functionality"""
    
    def __init__(self, chrome_debug_port=9222, config=None):
        self.chrome_debug_port = chrome_debug_port
        self.config = config or {}
        self.driver = None
        self._chrome_host = self._detect_chrome_host()
        
        # Get timing configuration
        self.timing = self.config.get('timing', {})
        self.default_timeout = self.timing.get('default_timeout', 10)
        self.element_wait_timeout = self.timing.get('element_wait_timeout', 10)
    
    def _detect_chrome_host(self):
        """Detect the correct Chrome host (for Docker compatibility)"""
        import requests
        
        if not self.config.get('options', {}).get('auto_detect_chrome_host', True):
            return '127.0.0.1'
        
        hosts = ['127.0.0.1']
        
        # Add Windows host IP if available (for Docker on Windows)
        windows_host_ip = os.environ.get('WINDOWS_HOST_IP')
        if windows_host_ip:
            hosts.insert(0, windows_host_ip)
        
        # Add host.docker.internal for Docker
        hosts.append('host.docker.internal')
        
        for host in hosts:
            try:
                response = requests.get(f'http://{host}:{self.chrome_debug_port}/json', timeout=2)
                if response.status_code == 200:
                    logger.info(f"Chrome debug host detected: {host}")
                    return host
            except:
                continue
        
        logger.warning(f"Could not detect Chrome host, defaulting to 127.0.0.1")
        return '127.0.0.1'
    
    def _is_valid_chromedriver(self, filepath):
        """
        Check if file is a valid chromedriver executable
        
        Args:
            filepath: Path to file to check
            
        Returns:
            bool: True if valid chromedriver executable
        """
        # Get just the filename
        filename = os.path.basename(filepath)
        
        # Must be exactly named 'chromedriver' (no extension, no prefix)
        if filename != 'chromedriver':
            return False
        
        # Path must NOT contain these strings (they're documentation files)
        excluded_keywords = ['LICENSE', 'NOTICE', 'README', 'THIRD_PARTY']
        if any(keyword in filepath.upper() for keyword in excluded_keywords):
            logger.debug(f"Skipping documentation file: {filepath}")
            return False
        
        # Must exist
        if not os.path.isfile(filepath):
            return False
        
        # Must be executable
        if not os.access(filepath, os.X_OK):
            logger.debug(f"File not executable: {filepath}")
            return False
        
        # Extra check: should have executable bit set in stat
        try:
            st = os.stat(filepath)
            is_executable = bool(st.st_mode & stat.S_IXUSR)
            if not is_executable:
                logger.debug(f"No execute permission: {filepath}")
                return False
        except:
            pass
        
        # Try to check file size - chromedriver should be > 1MB
        try:
            size = os.path.getsize(filepath)
            if size < 1_000_000:  # Less than 1MB
                logger.debug(f"File too small to be chromedriver ({size} bytes): {filepath}")
                return False
        except:
            pass
        
        logger.info(f"✓ Valid chromedriver found: {filepath}")
        return True
    
    def _get_chromedriver_path(self):
        """Get the correct chromedriver executable path, fixing webdriver-manager issues"""
        try:
            # Let webdriver-manager download/find the driver
            driver_path = ChromeDriverManager().install()
            
            # Get the base directory where chromedriver should be
            if os.path.isdir(driver_path):
                search_dir = driver_path
            else:
                search_dir = os.path.dirname(driver_path)
            
            logger.info(f"Searching for chromedriver in: {search_dir}")
            
            # Search recursively for the actual chromedriver executable
            found_paths = []
            for root, dirs, files in os.walk(search_dir):
                for file in files:
                    # Only check files named exactly 'chromedriver'
                    if file == 'chromedriver':
                        full_path = os.path.join(root, file)
                        
                        # Fix permissions if needed
                        if not os.access(full_path, os.X_OK):
                            logger.info(f"Setting executable permission for: {full_path}")
                            os.chmod(full_path, os.stat(full_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                        
                        if self._is_valid_chromedriver(full_path):
                            found_paths.append(full_path)
            
            # Return the first valid chromedriver found
            if found_paths:
                logger.info(f"Using chromedriver: {found_paths[0]}")
                return found_paths[0]
            
            # If no valid chromedriver found, raise clear error
            raise FileNotFoundError(
                f"Could not find valid chromedriver executable in {search_dir}.\n"
                f"Please delete the cache and try again:\n"
                f"  rm -rf ~/.wdm/drivers/chromedriver"
            )
            
        except Exception as e:
            logger.error(f"Error getting chromedriver path: {e}")
            raise
        
    def connect_to_chrome(self):
        """Connect to existing Chrome instance via remote debugging"""
        try:
            logger.info(f"Attempting to connect to Chrome on {self._chrome_host}:{self.chrome_debug_port}...")
            
            chrome_options = Options()
            chrome_options.add_experimental_option(
                "debuggerAddress", 
                f"{self._chrome_host}:{self.chrome_debug_port}"
            )
            
            logger.info("Creating Chrome WebDriver instance with automatic ChromeDriver management...")
            
            # Get the correct chromedriver path
            driver_path = self._get_chromedriver_path()
            logger.info(f"Using chromedriver at: {driver_path}")
            
            # Create service with the correct path
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            logger.info("Successfully connected to Chrome via remote debugging")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Chrome: {e}", exc_info=True)
            return False
    
    def find_tab_by_keywords(self, keywords):
        """
        Find and switch to tab matching any of the keywords
        
        Args:
            keywords: List of keywords to search for in title
            
        Returns:
            bool: True if tab found and switched, False otherwise
        """
        if not self.driver:
            logger.error("Driver not initialized")
            return False
        
        try:
            for window in self.driver.window_handles:
                self.driver.switch_to.window(window)
                title = self.driver.title.lower()
                
                if any(keyword.lower() in title for keyword in keywords):
                    logger.info(f"Found tab matching keywords {keywords}: {self.driver.title}")
                    return True
            
            logger.warning(f"Tab not found for keywords: {keywords}")
            return False
        except Exception as e:
            logger.error(f"Error finding tab: {e}")
            return False
    
    def wait_for_element(self, by, value, timeout=None):
        """
        Wait for element to be present
        
        Args:
            by: Selenium By locator type
            value: Locator value
            timeout: Maximum wait time in seconds (uses config if not provided)
            
        Returns:
            WebElement or None
        """
        if timeout is None:
            timeout = self.element_wait_timeout
            
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except Exception as e:
            logger.error(f"Element not found: {by}={value}, error: {e}")
            return None
    
    def wait_for_clickable(self, by, value, timeout=None):
        """
        Wait for element to be clickable
        
        Args:
            by: Selenium By locator type
            value: Locator value
            timeout: Maximum wait time in seconds (uses config if not provided)
            
        Returns:
            WebElement or None
        """
        if timeout is None:
            timeout = self.element_wait_timeout
            
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            return element
        except Exception as e:
            logger.error(f"Element not clickable: {by}={value}, error: {e}")
            return None
    
    def close(self):
        """Close the connection (but don't close Chrome)"""
        if self.driver:
            # We don't quit() because we're using existing Chrome
            self.driver = None
            logger.info("Extractor connection closed")