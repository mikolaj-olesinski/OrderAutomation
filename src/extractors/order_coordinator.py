"""
Order Coordinator
Orchestrates data extraction from BaseLinker and B2B Hendi
"""
import logging
from .baselinker_extractor import BaseLinkerExtractor
from .b2b_extractor import B2BExtractor

logger = logging.getLogger(__name__)

class OrderCoordinator:
    """Coordinates extraction from multiple sources"""
    
    def __init__(self, chrome_debug_port=9222, config=None):
        self.chrome_debug_port = chrome_debug_port
        self.config = config or {}
        self.baselinker_extractor = None
        self.b2b_extractor = None
    
    def extract_all_order_data(self):
        """
        Extract all order data from BaseLinker
        
        Returns:
            dict: Complete order data
        """
        order_data = {
            "success": False,
            "products": [],
            "payment_amount": None,
            "phone": None,
            "email": None,
            "address": None
        }
        
        try:
            # Initialize BaseLinker extractor with config
            self.baselinker_extractor = BaseLinkerExtractor(self.chrome_debug_port, self.config)
            
            # Connect to Chrome
            if not self.baselinker_extractor.connect_to_chrome():
                order_data["error"] = "Could not connect to Chrome"
                return order_data
            
            # Extract data from BaseLinker
            logger.info("Extracting data from BaseLinker...")
            baselinker_data = self.baselinker_extractor.extract_all_data()
            
            if not baselinker_data:
                order_data["error"] = "BaseLinker tab not found"
                self.baselinker_extractor.close()
                return order_data
            
            # Populate order data
            order_data["products"] = baselinker_data.get("products", [])
            order_data["payment_amount"] = baselinker_data.get("payment_amount")
            order_data["phone"] = baselinker_data.get("phone")
            order_data["email"] = baselinker_data.get("email")
            order_data["address"] = baselinker_data.get("address")
            
            order_data["success"] = True
            logger.info("Order data extraction completed successfully")
            
        except Exception as e:
            logger.error(f"Error during order data extraction: {e}", exc_info=True)
            order_data["error"] = str(e)
        
        finally:
            if self.baselinker_extractor:
                self.baselinker_extractor.close()
        
        return order_data
    
    def import_products_to_b2b(self, products):
        """
        Import products to B2B Hendi
        
        Args:
            products: List of dicts with 'sku' and 'quantity' keys
            
        Returns:
            dict: Result
        """
        try:
            # Initialize B2B extractor with config
            self.b2b_extractor = B2BExtractor(self.chrome_debug_port, self.config)
            
            # Connect to Chrome
            if not self.b2b_extractor.connect_to_chrome():
                return {
                    "success": False,
                    "error": "Could not connect to Chrome"
                }
            
            # Import products
            success = self.b2b_extractor.import_products(products)
            
            if success:
                return {
                    "success": True,
                    "message": f"Successfully imported {len(products)} products to B2B Hendi"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to import products"
                }
                
        except Exception as e:
            logger.error(f"Error importing products: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
        
        finally:
            if self.b2b_extractor:
                self.b2b_extractor.close()
    
    def complete_order_with_address(self, products, address_data, payment_amount=None):
        """
        Complete order: import products, fill delivery address, and select payment method
        
        Args:
            products: List of dicts with 'sku' and 'quantity' keys
            address_data: Dict with address fields
            payment_amount: Payment amount (optional)
            
        Returns:
            dict: Result
        """
        try:
            # Initialize B2B extractor with config
            self.b2b_extractor = B2BExtractor(self.chrome_debug_port, self.config)
            
            # Connect to Chrome
            if not self.b2b_extractor.connect_to_chrome():
                return {
                    "success": False,
                    "error": "Could not connect to Chrome"
                }
            
            # Import products
            logger.info("Importing products...")
            success = self.b2b_extractor.import_products(products)
            
            if not success:
                return {
                    "success": False,
                    "error": "Failed to import products"
                }
            
            # Fill delivery address
            logger.info("Filling delivery address...")
            success = self.b2b_extractor.fill_delivery_address(address_data)
            
            if not success:
                return {
                    "success": False,
                    "error": "Failed to fill delivery address"
                }
            
            # Select payment method
            logger.info("Selecting payment method...")
            success = self.b2b_extractor.select_payment_method(payment_amount)
            
            if not success:
                return {
                    "success": False,
                    "error": "Failed to select payment method"
                }
            
            return {
                "success": True,
                "message": f"Order completed: {len(products)} products imported, address filled, and payment method selected"
            }
                
        except Exception as e:
            logger.error(f"Error completing order: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
        
        finally:
            if self.b2b_extractor:
                self.b2b_extractor.close()