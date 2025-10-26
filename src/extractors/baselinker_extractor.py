"""
BaseLinker Extractor
Extracts order information from BaseLinker tab
"""
from selenium.webdriver.common.by import By
import re
import logging
from .base_extractor import BaseExtractor

logger = logging.getLogger(__name__)

class BaseLinkerExtractor(BaseExtractor):
    """Extractor for BaseLinker order data"""
    
    BASELINKER_KEYWORDS = ["baselinker", "base", "linker"]
    
    def __init__(self, chrome_debug_port=9222, config=None):
        super().__init__(chrome_debug_port, config)
        self.selectors = self.config.get('baselinker_selectors', {})
        self.patterns = self.config.get('regex_patterns', {}).get('baselinker', {})
        self.data_processing = self.config.get('data_processing', {})
    
    def find_baselinker_tab(self):
        """Find and switch to BaseLinker tab"""
        keywords = self.config.get('baselinker_keywords', self.BASELINKER_KEYWORDS)
        return self.find_tab_by_keywords(keywords)
    
    def extract_product_data(self):
        """
        Extract product data (SKU and quantity) from BaseLinker
        
        Returns:
            list: List of dicts with 'sku' and 'quantity' keys
        """
        products = []
        try:
            container_id = self.selectors.get('products_container', 'sale_items_container')
            container = self.driver.find_element(By.ID, container_id)
            rows = container.find_elements(By.TAG_NAME, 'tr')
            
            sku_pattern = self.patterns.get('sku', r'SKU\s*([A-Za-z0-9\-\.]+)')
            quantity_pattern = self.patterns.get('quantity', r'(\d+)\s+\d+\.\d+ PLN')
            remove_prefix = self.data_processing.get('remove_sku_prefix', 'H-')
            
            for row in rows[1:]:  # Skip header row
                text = row.text
                
                # Extract SKU
                sku_match = re.search(sku_pattern, text)
                
                if sku_match:
                    sku = sku_match.group(1).strip()
                    
                    # Remove prefix if configured and present
                    if remove_prefix and sku.startswith(remove_prefix):
                        sku = sku[len(remove_prefix):]
                    
                    # Extract quantity
                    quantity_match = re.search(quantity_pattern, text)
                    
                    if quantity_match:
                        quantity = quantity_match.group(1)
                        logger.info(f"Found product: SKU={sku}, Quantity={quantity}")
                        products.append({"sku": sku, "quantity": quantity})
            
            logger.info(f"Extracted {len(products)} products from BaseLinker")
            return products
            
        except Exception as e:
            logger.error(f"Failed to extract product data: {e}")
            return []
    
    def extract_payment_amount(self):
        """
        Extract payment amount from BaseLinker.
        - If NOT fully paid: returns "0" (leave B2B payment field empty)
        - If fully paid: returns paid amount (to fill in B2B)
        
        Returns:
            str: Payment amount or "0", or None on error
        """
        try:
            paid_selector = self.selectors.get('paid_amount', 'span[data-tid="editPayment"]')
            price_pattern = self.patterns.get('price_amount', r'([\d,]+\.?\d*)')
            
            # Get already paid amount
            try:
                paid_element = self.driver.find_element(By.CSS_SELECTOR, paid_selector)
                paid_text = paid_element.text
                paid_match = re.search(price_pattern, paid_text)
                paid_amount = float(paid_match.group(1).replace(',', '.')) if paid_match else 0.0
                logger.info(f"Already paid amount: {paid_amount} PLN")
            except Exception as e:
                logger.warning(f"Could not extract paid amount, assuming 0: {e}")
                paid_amount = 0.0
            
            # Get total order amount
            total_price_id = self.selectors.get('total_price', 'sale_total_price')
            price_element = self.driver.find_element(By.ID, total_price_id)
            price_text = price_element.text
            
            # Extract number from "2081.94 PLN"
            total_match = re.search(price_pattern, price_text)
            if total_match:
                total_amount = float(total_match.group(1).replace(',', '.'))
                logger.info(f"Total order amount: {total_amount} PLN")
                
                # Check if fully paid
                if paid_amount >= total_amount and paid_amount > 0:
                    logger.info(f"Order fully paid ({paid_amount} PLN) - returning paid amount")
                    return str(paid_amount)
                else:
                    logger.info(f"Order NOT fully paid ({paid_amount}/{total_amount}) - returning 0")
                    return "0"
            
            logger.warning("Total amount not found in element")
            return None
            
        except Exception as e:
            logger.error(f"Failed to extract payment amount: {e}")
            return None
    
    def extract_phone_number(self):
        """
        Extract phone number from BaseLinker
        
        Returns:
            str: Phone number without spaces and configured prefix, or None
        """
        try:
            phone_id = self.selectors.get('phone', 'oms_info_phone')
            remove_prefix = self.data_processing.get('remove_phone_prefix', '+48')
            
            phone_data = self.driver.find_element(By.ID, phone_id)
            phone_number = phone_data.text.replace(' ', '')
            
            # Remove prefix if configured and present
            if remove_prefix and phone_number.startswith(remove_prefix):
                phone_number = phone_number[len(remove_prefix):]
            
            logger.info(f"Phone number: {phone_number}")
            return phone_number
            
        except Exception as e:
            logger.error(f"Failed to extract phone number: {e}")
            return None
    
    def extract_email(self):
        """
        Extract email from BaseLinker
        
        Returns:
            str: Email address or None
        """
        try:
            email_id = self.selectors.get('email', 'oms_info_email')
            email_data = self.driver.find_element(By.ID, email_id)
            email = email_data.text
            logger.info(f"Email: {email}")
            return email
            
        except Exception as e:
            logger.error(f"Failed to extract email: {e}")
            return None
    
    def extract_address(self):
        """
        Extract delivery address data from BaseLinker
        
        Returns:
            dict: Address data with keys: name, company, address, city, postal_code
                  or None if extraction fails
        """
        try:
            address_selectors = self.selectors.get('address', {})
            
            name = self.driver.find_element(By.ID, address_selectors.get('fullname', 'oms_delivery_delivery_fullname')).text
            company = self.driver.find_element(By.ID, address_selectors.get('company', 'oms_delivery_delivery_company')).text
            address = self.driver.find_element(By.ID, address_selectors.get('street', 'oms_delivery_delivery_address')).text
            city = self.driver.find_element(By.ID, address_selectors.get('city', 'oms_delivery_delivery_city')).text
            postal_code = self.driver.find_element(By.ID, address_selectors.get('postcode', 'oms_delivery_delivery_postcode')).text
            
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
    
    def extract_b2b_number(self):
        """
        Extract B2B order number from BaseLinker extra field
        
        Returns:
            str: B2B order number or None if not set or in skip list
        """
        try:
            b2b_field_id = self.selectors.get('b2b_number_field', 'oms_info_extra_field_1')
            skip_values = self.data_processing.get('skip_b2b_number_values', ['...', ''])
            
            b2b_element = self.driver.find_element(By.ID, b2b_field_id)
            b2b_number = b2b_element.text.strip()
            
            # Skip if in skip list
            if b2b_number in skip_values:
                logger.info("B2B number not set in BaseLinker")
                return None
            
            logger.info(f"B2B Number from BaseLinker: {b2b_number}")
            return b2b_number
            
        except Exception as e:
            logger.error(f"Failed to extract B2B number from BaseLinker: {e}")
            return None
    
    def extract_all_data(self):
        """
        Extract all available data from BaseLinker tab
        
        Returns:
            dict: All extracted data
        """
        if not self.find_baselinker_tab():
            logger.error("BaseLinker tab not found")
            return None
        
        return {
            "products": self.extract_product_data(),
            "payment_amount": self.extract_payment_amount(),
            "phone": self.extract_phone_number(),
            "email": self.extract_email(),
            "address": self.extract_address()
        }