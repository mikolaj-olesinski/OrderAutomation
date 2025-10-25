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
    
    def find_baselinker_tab(self):
        """Find and switch to BaseLinker tab"""
        return self.find_tab_by_keywords(self.BASELINKER_KEYWORDS)
    
    def extract_product_data(self):
        """
        Extract product data (SKU and quantity) from BaseLinker
        
        Returns:
            list: List of dicts with 'sku' and 'quantity' keys
        """
        products = []
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
                    
                    # Remove H- prefix if present
                    if sku.startswith('H-'):
                        sku = sku[2:]
                    
                    # Extract quantity
                    quantity_pattern = r'(\d+)\s+\d+\.\d+ PLN'
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
        Extract payment amount from BaseLinker
        
        Returns:
            str: Payment amount (e.g., "67.95") or None
        """
        try:
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
        """
        Extract phone number from BaseLinker
        
        Returns:
            str: Phone number without spaces and +48 prefix, or None
        """
        try:
            phone_data = self.driver.find_element(By.ID, 'oms_info_phone')
            phone_number = phone_data.text.replace(' ', '')
            
            # Remove +48 prefix if present
            if phone_number.startswith('+48'):
                phone_number = phone_number[3:]
            
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
            email_data = self.driver.find_element(By.ID, 'oms_info_email')
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
    
    def extract_b2b_number(self):
        """
        Extract B2B order number from BaseLinker extra field
        
        Returns:
            str: B2B order number or None if not set or just "..."
        """
        try:
            b2b_element = self.driver.find_element(By.ID, 'oms_info_extra_field_1')
            b2b_number = b2b_element.text.strip()
            
            # Skip if it's just "..." or empty
            if b2b_number == '...' or not b2b_number:
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
            "address": self.extract_address(),
            "b2b_number": self.extract_b2b_number()
        }