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
    
    def __init__(self, chrome_debug_port=9222, config=None):
        super().__init__(chrome_debug_port, config)
        self.selectors = self.config.get('b2b_selectors', {})
        self.patterns = self.config.get('regex_patterns', {}).get('b2b', {})
        self.data_processing = self.config.get('data_processing', {})
        self.csv_config = self.config.get('csv_config', {})
        self.payment_methods = self.config.get('payment_methods', {})
        
    def find_b2b_hendi_tab(self):
        """Find and switch to B2B Hendi tab"""
        keywords = self.config.get('b2b_keywords', self.B2B_KEYWORDS)
        return self.find_tab_by_keywords(keywords)
    
    def extract_b2b_number(self):
        """
        Extract B2B order number from B2B Hendi tab
        
        Returns:
            str: B2B order number (e.g., "20451149") or None
        """
        try:
            container_class = self.selectors.get('order_settings_container', 'he-order-settings')
            pattern = self.patterns.get('order_number', r'Numer:\s*(\d+)\s*\/\s*(\d+)')
            
            container = self.driver.find_element(By.CLASS_NAME, container_class)
            text = container.text
            
            b2b_match = re.search(pattern, text)
            
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
            import_button_selector = self.selectors.get('import_button', 
                'button.jsShowModalButton[data-modal=".jsImportProductsModal"]')
            modal_class = self.selectors.get('import_modal', '.jsImportProductsModal')
            modal_delay = self.timing.get('modal_open_delay', 1)
            
            # Find and click the import button
            import_button = self.wait_for_clickable(
                By.CSS_SELECTOR, 
                import_button_selector,
                timeout=self.element_wait_timeout
            )
            
            if not import_button:
                logger.error("Import button not found")
                return False
            
            import_button.click()
            logger.info("Clicked 'Importuj produkty' button")
            
            time.sleep(modal_delay)
            
            # Check if modal appeared
            try:
                modal = self.driver.find_element(By.CSS_SELECTOR, modal_class)
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
            delimiter = self.csv_config.get('delimiter', ',')
            headers = self.csv_config.get('headers', ['SKU', 'Quantity'])
            encoding = self.csv_config.get('encoding', 'utf-8')
            
            if csv_path is None:
                temp_dir = tempfile.gettempdir()
                csv_path = os.path.join(temp_dir, 'products.csv')
            
            with open(csv_path, 'w', newline='', encoding=encoding) as f:
                writer = csv.writer(f, delimiter=delimiter)
                
                # Header
                writer.writerow(headers)
                
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
            file_input_selector = self.selectors.get('file_input', 'input[type="file"]')
            continue_button_selector = self.selectors.get('continue_button',
                'button.jsImportNextStepButton[type="submit"][form="import-form"]')
            add_to_cart_selector = self.selectors.get('add_to_cart_button',
                'button.jsManyProductsToCart[type="submit"]')
            checkout_selector = self.selectors.get('checkout_button',
                'button.jsCheckoutButton[type="submit"]')
            new_address_checkbox_id = self.selectors.get('new_address_checkbox', 'new_delivery_address')
            
            # Get timing delays
            after_upload_delay = self.timing.get('after_file_upload_delay', 1)
            between_steps_delay = self.timing.get('between_steps_delay', 2)
            
            # Find file input in modal
            file_input = self.wait_for_element(
                By.CSS_SELECTOR, 
                file_input_selector,
                timeout=self.element_wait_timeout
            )
            
            if not file_input:
                logger.error("File input not found in modal")
                return False
            
            # Send file path to input
            file_input.send_keys(csv_path)
            logger.info(f"File uploaded: {csv_path}")
            
            time.sleep(after_upload_delay)
            
            # First click: "Kontynuuj" button
            kontynuuj_button = self.wait_for_clickable(
                By.CSS_SELECTOR,
                continue_button_selector,
                timeout=self.element_wait_timeout
            )
            
            if not kontynuuj_button:
                logger.error("'Kontynuuj' button not found (first click)")
                return False
            
            kontynuuj_button.click()
            logger.info("Clicked 'Kontynuuj' button (first time)")
            
            time.sleep(between_steps_delay)
            
            # Second click: "Kontynuuj" button again
            kontynuuj_button_2 = self.wait_for_clickable(
                By.CSS_SELECTOR,
                continue_button_selector,
                timeout=self.element_wait_timeout
            )
            
            if not kontynuuj_button_2:
                logger.error("'Kontynuuj' button not found (second click)")
                return False
            
            kontynuuj_button_2.click()
            logger.info("Clicked 'Kontynuuj' button (second time)")
            
            time.sleep(between_steps_delay)
            
            # Third click: "Dodaj produkty do koszyka" button
            add_to_cart_button = self.wait_for_clickable(
                By.CSS_SELECTOR,
                add_to_cart_selector,
                timeout=self.element_wait_timeout
            )
            
            if not add_to_cart_button:
                logger.error("'Dodaj produkty do koszyka' button not found")
                return False
            
            add_to_cart_button.click()
            logger.info("Clicked 'Dodaj produkty do koszyka' button")
            
            time.sleep(between_steps_delay)
            
            # Fourth click: "Przejdź do zamówienia" button
            checkout_button = self.wait_for_clickable(
                By.CSS_SELECTOR,
                checkout_selector,
                timeout=self.element_wait_timeout
            )
            
            if not checkout_button:
                logger.error("'Przejdź do zamówienia' button not found")
                return False
            
            checkout_button.click()
            logger.info("Clicked 'Przejdź do zamówienia' button")
            
            time.sleep(between_steps_delay)
            
            # Check and toggle "Wprowadź nowy adres dostawy" checkbox if not checked
            try:
                new_address_checkbox = self.driver.find_element(
                    By.ID,
                    new_address_checkbox_id
                )
                
                if not new_address_checkbox.is_selected():
                    checkbox_label = self.driver.find_element(
                        By.CSS_SELECTOR,
                        f'label[for="{new_address_checkbox_id}"]'
                    )
                    checkbox_label.click()
                    logger.info("Checked 'Wprowadź nowy adres dostawy' checkbox")
                    time.sleep(after_upload_delay)
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
                - name, phone, email, street, street_no, street_flat, zip, city
                
        Returns:
            bool: True if form filled and submitted successfully, False otherwise
        """
        try:
            modal_selector = self.selectors.get('address_modal', '.jsAddAddressModal')
            save_button_selector = self.selectors.get('save_address_button',
                'button[type="submit"][form="user-address-form"]')
            form_fields = self.selectors.get('address_form_fields', {})
            
            form_submit_delay = self.timing.get('form_submit_delay', 2)
            after_click_delay = self.timing.get('after_click_delay', 1)
            use_javascript = self.config.get('options', {}).get('use_javascript_for_form_filling', True)
            
            # Wait for modal to appear
            modal = self.wait_for_element(
                By.CSS_SELECTOR,
                modal_selector,
                timeout=self.element_wait_timeout
            )
            
            if not modal:
                logger.error("Address modal not found")
                return False
            
            logger.info("Address modal found, filling form...")
            
            # Helper function to fill input
            def fill_input(name, value):
                try:
                    field_name = form_fields.get(name.replace('address_data[', '').replace(']', ''), name)
                    input_element = self.driver.find_element(By.NAME, field_name)
                    input_element.clear()
                    
                    if use_javascript:
                        # Use JavaScript to set value to preserve Polish characters
                        self.driver.execute_script(
                            "arguments[0].value = arguments[1];",
                            input_element,
                            str(value)
                        )
                        # Trigger input event
                        self.driver.execute_script(
                            "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));",
                            input_element
                        )
                    else:
                        input_element.send_keys(str(value))
                    
                    logger.info(f"Filled {field_name}: {value}")
                    return True
                except Exception as e:
                    logger.error(f"Failed to fill {field_name}: {e}")
                    return False
            
            # Fill all fields
            default_building = self.data_processing.get('default_building_number', '.')
            
            fill_input('name', address_data.get('name', ''))
            fill_input('phone', address_data.get('phone', ''))
            fill_input('email', address_data.get('email', ''))
            fill_input('street', address_data.get('street', ''))
            fill_input('street_no', address_data.get('street_no', default_building))
            
            if address_data.get('street_flat'):
                fill_input('street_flat', address_data.get('street_flat'))
            
            fill_input('zip', address_data.get('zip', ''))
            fill_input('city', address_data.get('city', ''))
            
            time.sleep(after_click_delay)
            
            # Click "Zapisz" button
            save_button = self.wait_for_clickable(
                By.CSS_SELECTOR,
                save_button_selector,
                timeout=self.element_wait_timeout
            )
            
            if not save_button:
                logger.error("Save button not found")
                return False
            
            save_button.click()
            logger.info("Clicked 'Zapisz' button")
            
            time.sleep(form_submit_delay)
            return True
            
        except Exception as e:
            logger.error(f"Failed to fill delivery address: {e}")
            return False
    
    def select_payment_method(self, payment_amount=None):
        """
        Select payment method based on payment amount
        
        Args:
            payment_amount: Payment amount from BaseLinker (str)
            
        Returns:
            bool: True if payment method selected successfully
        """
        try:
            payment_selectors = self.selectors.get('payment', {})
            bank_transfer_value = self.payment_methods.get('bank_transfer_value', '29')
            cash_on_delivery_value = self.payment_methods.get('cash_on_delivery_value', '21')
            
            payment_delay = self.timing.get('payment_section_delay', 2)
            after_click_delay = self.timing.get('after_click_delay', 1)
            
            time.sleep(payment_delay)
            
            # Convert payment_amount to float
            try:
                amount = float(payment_amount) if payment_amount else 0.0
            except:
                amount = 0.0
            
            if amount > 0:
                # Order paid - select bank transfer
                logger.info(f"Order already paid ({amount} PLN) - selecting 'Przelew 3 dni'")
                
                try:
                    przelew_radio = self.driver.find_element(
                        By.CSS_SELECTOR,
                        payment_selectors.get('bank_transfer_radio',
                            f'input[type="radio"][name="payment_id"][value="{bank_transfer_value}"]')
                    )
                    
                    if not przelew_radio.is_selected():
                        self.driver.execute_script("arguments[0].click();", przelew_radio)
                        logger.info("Selected 'Przelew 3 dni' payment method")
                        time.sleep(after_click_delay)
                    else:
                        logger.info("'Przelew 3 dni' payment method already selected")
                        
                except Exception as e:
                    logger.error(f"Could not select 'Przelew 3 dni': {e}")
                    # Try clicking label
                    try:
                        label = self.driver.find_element(
                            By.CSS_SELECTOR,
                            payment_selectors.get('bank_transfer_label', f'label[for="{bank_transfer_value}"]')
                        )
                        self.driver.execute_script("arguments[0].click();", label)
                        logger.info("Selected 'Przelew 3 dni' using label click")
                        time.sleep(after_click_delay)
                    except Exception as e2:
                        logger.error(f"Could not click 'Przelew 3 dni' label: {e2}")
                        return False
                        
            else:
                # Order NOT paid - select cash on delivery
                logger.info("Order NOT paid - selecting 'Pobranie' with empty field")
                
                try:
                    pobranie_radio = self.driver.find_element(
                        By.CSS_SELECTOR,
                        payment_selectors.get('cash_on_delivery_radio',
                            f'input[type="radio"][name="payment_id"][value="{cash_on_delivery_value}"]')
                    )
                    
                    if not pobranie_radio.is_selected():
                        self.driver.execute_script("arguments[0].click();", pobranie_radio)
                        logger.info("Selected 'Pobranie' payment method")
                        time.sleep(after_click_delay)
                    else:
                        logger.info("'Pobranie' payment method already selected")
                    
                    # Make sure field is empty
                    try:
                        payment_input = self.driver.find_element(
                            By.NAME,
                            payment_selectors.get('cash_amount_field',
                                f'payment_params[custom_payment_price][{cash_on_delivery_value}]')
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
                            payment_selectors.get('cash_on_delivery_label', f'label[for="{cash_on_delivery_value}"]')
                        )
                        self.driver.execute_script("arguments[0].click();", label)
                        logger.info("Selected 'Pobranie' using label click")
                        time.sleep(after_click_delay)
                    except Exception as e2:
                        logger.error(f"Could not click 'Pobranie' label: {e2}")
                        return False
            
            time.sleep(after_click_delay)
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