"""
B2B Hendi Extractor
Extracts order information and handles imports on B2B Hendi tab
"""
from selenium.webdriver.common.by import By
import re
import csv
import tempfile
import os
import time
import logging
from .base_extractor import BaseExtractor

logger = logging.getLogger(__name__)

class B2BExtractor(BaseExtractor):
    """Extractor for B2B Hendi operations"""
    
    B2B_KEYWORDS = ["b2b", "hendi"]
    
    def find_b2b_hendi_tab(self):
        """Find and switch to B2B Hendi tab"""
        return self.find_tab_by_keywords(self.B2B_KEYWORDS)
    
    def extract_b2b_number(self):
        """
        Extract B2B order number from B2B Hendi tab
        
        Returns:
            str: B2B order number (e.g., "20451149") or None
        """
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
    
    def click_import_products_button(self):
        """
        Click the 'Importuj produkty' button to open import modal
        
        Returns:
            bool: True if modal opened successfully, False otherwise
        """
        try:
            # Find and click the import button
            import_button = self.wait_for_clickable(
                By.CSS_SELECTOR, 
                'button.jsShowModalButton[data-modal=".jsImportProductsModal"]',
                timeout=10
            )
            
            if not import_button:
                logger.error("Import button not found")
                return False
            
            import_button.click()
            logger.info("Clicked 'Importuj produkty' button")
            
            # Wait a bit for modal to appear
            time.sleep(1)
            
            # Check if modal appeared
            try:
                modal = self.driver.find_element(By.CLASS_NAME, 'jsImportProductsModal')
                if modal.is_displayed():
                    logger.info("Import modal opened successfully")
                    return True
                else:
                    logger.warning("Modal found but not displayed")
                    return False
            except:
                logger.warning("Modal not found after clicking button")
                return False
                
        except Exception as e:
            logger.error(f"Failed to click import button: {e}")
            return False
    
    def create_csv_from_products(self, products, csv_path=None):
        """
        Create CSV file from products list
        
        Args:
            products: List of dicts with 'sku' and 'quantity' keys
            csv_path: Optional path for CSV file. If None, uses temp directory
            
        Returns:
            str: Path to created CSV file or None if failed
        """
        try:
            # Use temp directory that works on all OS
            if csv_path is None:
                temp_dir = tempfile.gettempdir()
                csv_path = os.path.join(temp_dir, 'products.csv')
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=',')
                
                # Header
                writer.writerow(['SKU', 'Quantity'])
                
                # Products
                for product in products:
                    writer.writerow([product['sku'], product['quantity']])
            
            logger.info(f"CSV file created: {csv_path} with {len(products)} products")
            return csv_path
            
        except Exception as e:
            logger.error(f"Failed to create CSV: {e}")
            return None
    
    def upload_csv_to_modal(self, csv_path):
        """
        Upload CSV file to the import modal and complete the import process
        
        Args:
            csv_path: Path to CSV file to upload
            
        Returns:
            bool: True if upload successful, False otherwise
        """
        try:
            # Find file input in modal
            file_input = self.wait_for_element(
                By.CSS_SELECTOR, 
                'input[type="file"]',
                timeout=10
            )
            
            if not file_input:
                logger.error("File input not found in modal")
                return False
            
            # Send file path to input
            file_input.send_keys(csv_path)
            logger.info(f"File uploaded: {csv_path}")
            
            time.sleep(1)
            
            # First click: Find and click the "Kontynuuj" button
            kontynuuj_button = self.wait_for_clickable(
                By.CSS_SELECTOR,
                'button.jsImportNextStepButton[type="submit"][form="import-form"]',
                timeout=10
            )
            
            if not kontynuuj_button:
                logger.error("'Kontynuuj' button not found (first click)")
                return False
            
            kontynuuj_button.click()
            logger.info("Clicked 'Kontynuuj' button (first time)")
            
            time.sleep(2)
            
            # Second click: Find and click the "Kontynuuj" button again
            kontynuuj_button_2 = self.wait_for_clickable(
                By.CSS_SELECTOR,
                'button.jsImportNextStepButton[type="submit"][form="import-form"]',
                timeout=10
            )
            
            if not kontynuuj_button_2:
                logger.error("'Kontynuuj' button not found (second click)")
                return False
            
            kontynuuj_button_2.click()
            logger.info("Clicked 'Kontynuuj' button (second time)")
            
            time.sleep(2)
            
            # Third click: Find and click "Dodaj produkty do koszyka" button
            add_to_cart_button = self.wait_for_clickable(
                By.CSS_SELECTOR,
                'button.jsManyProductsToCart[type="submit"]',
                timeout=10
            )
            
            if not add_to_cart_button:
                logger.error("'Dodaj produkty do koszyka' button not found")
                return False
            
            add_to_cart_button.click()
            logger.info("Clicked 'Dodaj produkty do koszyka' button")
            
            time.sleep(2)
            
            # Fourth click: Find and click "Przejdź do zamówienia" button
            checkout_button = self.wait_for_clickable(
                By.CSS_SELECTOR,
                'button.jsCheckoutButton[type="submit"]',
                timeout=10
            )
            
            if not checkout_button:
                logger.error("'Przejdź do zamówienia' button not found")
                return False
            
            checkout_button.click()
            logger.info("Clicked 'Przejdź do zamówienia' button")
            
            time.sleep(2)
            
            # Check and toggle "Wprowadź nowy adres dostawy" checkbox if not checked
            try:
                new_address_checkbox = self.driver.find_element(
                    By.ID,
                    'new_delivery_address'
                )
                
                if not new_address_checkbox.is_selected():
                    # Click the label to toggle checkbox
                    checkbox_label = self.driver.find_element(
                        By.CSS_SELECTOR,
                        'label[for="new_delivery_address"]'
                    )
                    checkbox_label.click()
                    logger.info("Checked 'Wprowadź nowy adres dostawy' checkbox")
                    time.sleep(1)
                else:
                    logger.info("'Wprowadź nowy adres dostawy' checkbox already checked")
                    
            except Exception as e:
                logger.warning(f"Could not find or check new address checkbox: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload CSV: {e}")
            return False
    
    def fill_delivery_address(self, address_data):
        """
        Fill delivery address form in the modal
        
        Args:
            address_data: Dict with keys:
                - name: Company name (required)
                - phone: Phone number (required)
                - email: Email address (required)
                - street: Street name (required)
                - street_no: Building number (required)
                - street_flat: Apartment number (optional)
                - zip: Postal code (required)
                - city: City name (required)
                
        Returns:
            bool: True if form filled and submitted successfully, False otherwise
        """
        try:
            # Wait for modal to appear
            modal = self.wait_for_element(
                By.CSS_SELECTOR,
                '.jsAddAddressModal',
                timeout=10
            )
            
            if not modal:
                logger.error("Address modal not found")
                return False
            
            logger.info("Address modal found, filling form...")
            
            # Helper function to fill input with proper encoding
            def fill_input(name, value):
                try:
                    input_element = self.driver.find_element(By.NAME, name)
                    input_element.clear()
                    # Use JavaScript to set value to preserve Polish characters
                    self.driver.execute_script(
                        "arguments[0].value = arguments[1];",
                        input_element,
                        str(value)
                    )
                    # Trigger input event to ensure form validation
                    self.driver.execute_script(
                        "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));",
                        input_element
                    )
                    logger.info(f"Filled {name}: {value}")
                    return True
                except Exception as e:
                    logger.error(f"Failed to fill {name}: {e}")
                    return False
            
            # Fill all fields
            fill_input('address_data[name]', address_data.get('name', ''))
            fill_input('address_data[phone]', address_data.get('phone', ''))
            fill_input('address_data[email]', address_data.get('email', ''))
            fill_input('address_data[street]', address_data.get('street', ''))
            fill_input('address_data[street_no]', address_data.get('street_no', '.'))
            
            # Fill apartment number if provided
            if address_data.get('street_flat'):
                fill_input('address_data[street_flat]', address_data.get('street_flat'))
            
            fill_input('address_data[zip]', address_data.get('zip', ''))
            fill_input('address_data[city]', address_data.get('city', ''))
            
            time.sleep(1)
            
            # Click "Zapisz" button to submit the form
            save_button = self.wait_for_clickable(
                By.CSS_SELECTOR,
                'button[type="submit"][form="user-address-form"]',
                timeout=10
            )
            
            if not save_button:
                logger.error("Save button not found")
                return False
            
            save_button.click()
            logger.info("Clicked 'Zapisz' button")
            
            time.sleep(2)
            return True
            
        except Exception as e:
            logger.error(f"Failed to fill delivery address: {e}")
            return False
    
    def select_payment_method(self, payment_amount=None):
            """
            Select payment method based on payment amount:
            - If amount is "0" or not provided: Select "Pobranie" (Cash on Delivery) - leave field empty
            - If amount > 0: Select "Przelew 3 dni" (Bank Transfer)
            
            Args:
                payment_amount: Payment amount from BaseLinker (str)
                
            Returns:
                bool: True if payment method selected successfully, False otherwise
            """
            try:
                # Wait for payment section to be visible
                time.sleep(2)
                
                # Convert payment_amount to float for comparison
                try:
                    amount = float(payment_amount) if payment_amount else 0.0
                except:
                    amount = 0.0
                
                # Determine which payment method to select
                if amount > 0:
                    # Order is already paid - select "Przelew 3 dni" (Bank Transfer)
                    logger.info(f"Order already paid ({amount} PLN) - selecting 'Przelew 3 dni'")
                    
                    try:
                        przelew_radio = self.driver.find_element(
                            By.CSS_SELECTOR,
                            'input[type="radio"][name="payment_id"][value="29"]'
                        )
                        
                        if not przelew_radio.is_selected():
                            self.driver.execute_script("arguments[0].click();", przelew_radio)
                            logger.info("Selected 'Przelew 3 dni' payment method")
                            time.sleep(1)
                        else:
                            logger.info("'Przelew 3 dni' payment method already selected")
                            
                    except Exception as e:
                        logger.error(f"Could not select 'Przelew 3 dni': {e}")
                        # Try clicking label
                        try:
                            label = self.driver.find_element(
                                By.CSS_SELECTOR,
                                'label[for="29"]'
                            )
                            self.driver.execute_script("arguments[0].click();", label)
                            logger.info("Selected 'Przelew 3 dni' using label click")
                            time.sleep(1)
                        except Exception as e2:
                            logger.error(f"Could not click 'Przelew 3 dni' label: {e2}")
                            return False
                            
                else:
                    # Order NOT paid - select "Pobranie" (Cash on Delivery) with empty field
                    logger.info("Order NOT paid - selecting 'Pobranie' with empty field")
                    
                    try:
                        pobranie_radio = self.driver.find_element(
                            By.CSS_SELECTOR,
                            'input[type="radio"][name="payment_id"][value="21"]'
                        )
                        
                        if not pobranie_radio.is_selected():
                            self.driver.execute_script("arguments[0].click();", pobranie_radio)
                            logger.info("Selected 'Pobranie' payment method")
                            time.sleep(1)
                        else:
                            logger.info("'Pobranie' payment method already selected")
                        
                        # Make sure the field is EMPTY (don't fill anything)
                        try:
                            payment_input = self.driver.find_element(
                                By.NAME,
                                'payment_params[custom_payment_price][21]'
                            )
                            payment_input.clear()
                            logger.info("Left 'Pobranie' amount field empty")
                        except Exception as e:
                            logger.warning(f"Could not clear payment field: {e}")
                            
                    except Exception as e:
                        logger.error(f"Could not select 'Pobranie': {e}")
                        # Try clicking label
                        try:
                            label = self.driver.find_element(
                                By.CSS_SELECTOR,
                                'label[for="21"]'
                            )
                            self.driver.execute_script("arguments[0].click();", label)
                            logger.info("Selected 'Pobranie' using label click")
                            time.sleep(1)
                        except Exception as e2:
                            logger.error(f"Could not click 'Pobranie' label: {e2}")
                            return False
                
                time.sleep(1)
                return True
                
            except Exception as e:
                logger.error(f"Failed to select payment method: {e}")
                return False
        
    def import_products(self, products):
        """
        Complete flow: open modal, create CSV, and upload
        
        Args:
            products: List of dicts with 'sku' and 'quantity' keys
            
        Returns:
            bool: True if all steps successful, False otherwise
        """
        # Step 1: Find B2B Hendi tab
        if not self.find_b2b_hendi_tab():
            logger.error("B2B Hendi tab not found")
            return False
        
        # Step 2: Open import modal
        if not self.click_import_products_button():
            logger.error("Failed to open import modal")
            return False
        
        # Step 3: Create CSV
        csv_path = self.create_csv_from_products(products)
        if not csv_path:
            logger.error("Failed to create CSV file")
            return False
        
        # Step 4: Upload CSV
        if not self.upload_csv_to_modal(csv_path):
            logger.error("Failed to upload CSV")
            return False
        
        logger.info(f"Successfully imported {len(products)} products to B2B Hendi")
        return True