"""
Order Data Extractor
Extracts order information from BaseLinker and B2B Hendi tabs
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import logging
import time

logger = logging.getLogger(__name__)

class OrderExtractor:
    def __init__(self, chrome_debug_port=9222):
        self.chrome_debug_port = chrome_debug_port
        self.driver = None
    
    def connect_to_chrome(self):
        """Connect to existing Chrome instance via remote debugging"""
        try:
            logger.info(f"Attempting to connect to Chrome on port {self.chrome_debug_port}...")
            
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{self.chrome_debug_port}")
            
            logger.info("Creating Chrome WebDriver instance...")
            # Selenium 4.6+ has built-in driver manager - no need for webdriver-manager
            self.driver = webdriver.Chrome(options=chrome_options)
            
            logger.info("Successfully connected to Chrome via remote debugging")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Chrome: {e}", exc_info=True)
            return False
    
    def find_baselinker_tab(self):
        """Find and switch to BaseLinker tab"""
        if not self.driver:
            return False
        
        try:
            for window in self.driver.window_handles:
                self.driver.switch_to.window(window)
                title = self.driver.title.lower()
                if "base" in title or "linker" in title:
                    logger.info(f"Found BaseLinker tab: {self.driver.title}")
                    return True
            
            logger.warning("BaseLinker tab not found")
            return False
        except Exception as e:
            logger.error(f"Error finding BaseLinker tab: {e}")
            return False
    
    def find_b2b_hendi_tab(self):
        """Find and switch to B2B Hendi tab"""
        if not self.driver:
            return False
        
        try:
            for window in self.driver.window_handles:
                self.driver.switch_to.window(window)
                title = self.driver.title.lower()
                if "b2b" in title and "hendi" in title:
                    logger.info(f"Found B2B Hendi tab: {self.driver.title}")
                    return True
            
            logger.warning("B2B Hendi tab not found")
            return False
        except Exception as e:
            logger.error(f"Error finding B2B Hendi tab: {e}")
            return False
    
    def extract_product_data(self):
        """Extract product data (SKU and quantity) from BaseLinker"""
        data = []
        try:
            container = self.driver.find_element(By.ID, 'sale_items_container')
            rows = container.find_elements(By.TAG_NAME, 'tr')
            
            for row in rows[1:]:  # Skip header row
                text = row.text
                
                # Extract SKU
                sku_pattern = r'SKU\s*([A-Za-z0-9\-\.]+)'
                sku_match = re.search(sku_pattern, text)
                if sku_match:
                    sku = sku_match.group(1).strip()
                    if sku.startswith('H-'):
                        sku = sku[2:]
                    
                    # Extract quantity
                    quantity_pattern = r'(\d+)\s+\d+\.\d+ PLN'
                    quantity_match = re.search(quantity_pattern, text)
                    
                    if quantity_match:
                        quantity = quantity_match.group(1)
                        logger.info(f"Found product: SKU={sku}, Quantity={quantity}")
                        data.append({"sku": sku, "quantity": quantity})
            
            return data
        except Exception as e:
            logger.error(f"Failed to extract product data: {e}")
            return []
    
    def extract_payment_amount(self):
        """Extract payment amount from BaseLinker"""
        try:
            # Try to find total price element
            price_element = self.driver.find_element(By.ID, 'sale_total_price')
            price_text = price_element.text
            
            # Extract number from "67.95 PLN"
            amount_match = re.search(r'([\d,]+\.\d+)', price_text)
            if amount_match:
                amount = amount_match.group(1)
                logger.info(f"Payment amount: {amount} PLN")
                return amount
            
            logger.warning("Payment amount not found in element")
            return None
        except Exception as e:
            logger.error(f"Failed to extract payment amount: {e}")
            return None
    
    def extract_phone_number(self):
        """Extract phone number from BaseLinker"""
        try:
            phone_data = self.driver.find_element(By.ID, 'oms_info_phone')
            phone_number = phone_data.text.replace(' ', '')
            
            if phone_number.startswith('+48'):
                phone_number = phone_number[3:]
            
            logger.info(f"Phone number: {phone_number}")
            return phone_number
        except Exception as e:
            logger.error(f"Failed to extract phone number: {e}")
            return None
    
    def extract_email(self):
        """Extract email from BaseLinker"""
        try:
            email_data = self.driver.find_element(By.ID, 'oms_info_email')
            email = email_data.text
            logger.info(f"Email: {email}")
            return email
        except Exception as e:
            logger.error(f"Failed to extract email: {e}")
            return None
    
    def extract_address(self):
        """Extract address data from BaseLinker"""
        try:
            name = self.driver.find_element(By.ID, 'oms_delivery_delivery_fullname').text
            company = self.driver.find_element(By.ID, 'oms_delivery_delivery_company').text
            address = self.driver.find_element(By.ID, 'oms_delivery_delivery_address').text
            city = self.driver.find_element(By.ID, 'oms_delivery_delivery_city').text
            postal_code = self.driver.find_element(By.ID, 'oms_delivery_delivery_postcode').text
            
            address_data = {
                "name": name,
                "company": company,
                "address": address,
                "city": city,
                "postal_code": postal_code
            }
            
            logger.info(f"Address extracted: {name}, {city}")
            return address_data
        except Exception as e:
            logger.error(f"Failed to extract address: {e}")
            return None
    
    def extract_b2b_number_from_baselinker(self):
        """Extract B2B order number from BaseLinker extra field"""
        try:
            b2b_element = self.driver.find_element(By.ID, 'oms_info_extra_field_1')
            b2b_number = b2b_element.text.strip()
            
            # Skip if it's just "..."
            if b2b_number == '...' or not b2b_number:
                logger.info("B2B number not set in BaseLinker")
                return None
            
            logger.info(f"B2B Number from BaseLinker: {b2b_number}")
            return b2b_number
        except Exception as e:
            logger.error(f"Failed to extract B2B number from BaseLinker: {e}")
            return None
    
    def extract_b2b_number(self):
        """Extract B2B order number from B2B Hendi tab"""
        try:
            container = self.driver.find_element(By.CLASS_NAME, 'he-order-settings')
            text = container.text
            
            # Pattern: Numer: 20451149 / 2024
            b2b_pattern = r'Numer:\s*(\d+)\s*\/\s*(\d+)'
            b2b_match = re.search(b2b_pattern, text)
            
            if b2b_match:
                b2b_number = b2b_match.group(1)
                year = b2b_match.group(2)
                logger.info(f"B2B Order Number: {b2b_number}/{year}")
                return b2b_number
            
            logger.warning("B2B order number not found")
            return None
        except Exception as e:
            logger.error(f"Failed to extract B2B number: {e}")
            return None
    
    def extract_all_order_data(self):
        """Extract all order data from BaseLinker and B2B Hendi"""
        order_data = {
            "success": False,
            "products": [],
            "payment_amount": None,
            "phone": None,
            "email": None,
            "address": None,
            "b2b_number": None
        }
        
        try:
            # Connect to Chrome
            if not self.connect_to_chrome():
                order_data["error"] = "Could not connect to Chrome"
                return order_data
            
            # Extract from BaseLinker
            if self.find_baselinker_tab():
                order_data["products"] = self.extract_product_data()
                order_data["payment_amount"] = self.extract_payment_amount()
                order_data["phone"] = self.extract_phone_number()
                order_data["email"] = self.extract_email()
                order_data["address"] = self.extract_address()
                order_data["b2b_number"] = self.extract_b2b_number_from_baselinker()
            else:
                order_data["error"] = "BaseLinker tab not found"
                return order_data
            
            # Extract from B2B Hendi (if tab exists and B2B number not in BaseLinker)
            if self.find_b2b_hendi_tab() and not order_data["b2b_number"]:
                b2b_num = self.extract_b2b_number()
                if b2b_num:
                    order_data["b2b_number"] = b2b_num
            
            order_data["success"] = True
            logger.info("Order data extraction completed successfully")
            
        except Exception as e:
            logger.error(f"Error during order data extraction: {e}")
            order_data["error"] = str(e)
        finally:
            # Don't close the driver - we're using existing Chrome
            pass
        
        return order_data
    
    def close(self):
        """Close the connection (but don't close Chrome)"""
        if self.driver:
            # We don't quit() because we're using existing Chrome
            self.driver = None