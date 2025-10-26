let statusInterval;
let logsInterval;

// Fetch and display backend logs
async function updateLogs() {
    try {
        const response = await fetch('/api/logs');
        const data = await response.json();
        
        if (data.logs && data.logs.length > 0) {
            const logContainer = document.getElementById('log-container');
            logContainer.innerHTML = '';
            
            data.logs.forEach(line => {
                const logEntry = document.createElement('div');
                logEntry.textContent = line.trim();
                
                if (line.includes('ERROR')) {
                    logEntry.style.color = '#ff6b6b';
                } else if (line.includes('WARNING')) {
                    logEntry.style.color = '#ffd93d';
                } else if (line.includes('SUCCESS')) {
                    logEntry.style.color = '#6bcf7f';
                }
                
                logContainer.appendChild(logEntry);
            });
            
            logContainer.scrollTop = logContainer.scrollHeight;
        }
    } catch (error) {
        console.error('Failed to fetch logs:', error);
    }
}

// Load configuration
async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        
        // General settings
        document.getElementById('chrome-path').value = config.chrome_path || '';
        document.getElementById('user-data-dir').value = config.chrome_user_data_dir || '';
        document.getElementById('debug-port').value = config.chrome_debug_port || 9222;
        document.getElementById('baselinker-url').value = config.baselinker_url || '';
        document.getElementById('b2b-url').value = config.b2b_hendi_url || '';
        document.getElementById('baselinker-keywords').value = (config.baselinker_keywords || []).join(', ');
        document.getElementById('b2b-keywords').value = (config.b2b_keywords || []).join(', ');

        // BaseLinker selectors
        const blSel = config.baselinker_selectors || {};
        document.getElementById('bl-products-container').value = blSel.products_container || '';
        document.getElementById('bl-total-price').value = blSel.total_price || '';
        document.getElementById('bl-paid-amount').value = blSel.paid_amount || '';
        document.getElementById('bl-phone').value = blSel.phone || '';
        document.getElementById('bl-email').value = blSel.email || '';
        document.getElementById('bl-b2b-field').value = blSel.b2b_number_field || '';
        
        const blAddr = blSel.address || {};
        document.getElementById('bl-addr-fullname').value = blAddr.fullname || '';
        document.getElementById('bl-addr-company').value = blAddr.company || '';
        document.getElementById('bl-addr-street').value = blAddr.street || '';
        document.getElementById('bl-addr-city').value = blAddr.city || '';
        document.getElementById('bl-addr-postcode').value = blAddr.postcode || '';

        // BaseLinker regex
        const blRegex = config.regex_patterns?.baselinker || {};
        document.getElementById('bl-regex-sku').value = blRegex.sku || '';
        document.getElementById('bl-regex-quantity').value = blRegex.quantity || '';
        document.getElementById('bl-regex-price').value = blRegex.price_amount || '';

        // B2B selectors
        const b2bSel = config.b2b_selectors || {};
        document.getElementById('b2b-order-container').value = b2bSel.order_settings_container || '';
        document.getElementById('b2b-import-btn').value = b2bSel.import_button || '';
        document.getElementById('b2b-import-modal').value = b2bSel.import_modal || '';
        document.getElementById('b2b-file-input').value = b2bSel.file_input || '';
        document.getElementById('b2b-continue-btn').value = b2bSel.continue_button || '';
        document.getElementById('b2b-add-cart-btn').value = b2bSel.add_to_cart_button || '';
        document.getElementById('b2b-checkout-btn').value = b2bSel.checkout_button || '';

        // B2B payment
        const paymentMethods = config.payment_methods || {};
        document.getElementById('b2b-payment-transfer').value = paymentMethods.bank_transfer_value || '';
        document.getElementById('b2b-payment-cash').value = paymentMethods.cash_on_delivery_value || '';

        // B2B regex
        const b2bRegex = config.regex_patterns?.b2b || {};
        document.getElementById('b2b-regex-order').value = b2bRegex.order_number || '';

        // CSV config
        const csvConf = config.csv_config || {};
        document.getElementById('csv-delimiter').value = csvConf.delimiter || ',';
        document.getElementById('csv-encoding').value = csvConf.encoding || 'utf-8';
        document.getElementById('csv-headers').value = (csvConf.headers || []).join(', ');

        // Timing
        const timing = config.timing || {};
        document.getElementById('timing-default').value = timing.default_timeout || 10;
        document.getElementById('timing-element').value = timing.element_wait_timeout || 10;
        document.getElementById('timing-click').value = timing.after_click_delay || 1;
        document.getElementById('timing-upload').value = timing.after_file_upload_delay || 1;
        document.getElementById('timing-steps').value = timing.between_steps_delay || 2;
        document.getElementById('timing-startup').value = timing.chrome_startup_delay || 2;
        document.getElementById('timing-modal').value = timing.modal_open_delay || 1;
        document.getElementById('timing-form').value = timing.form_submit_delay || 2;
        document.getElementById('timing-payment').value = timing.payment_section_delay || 2;

        // Data processing
        const dataProc = config.data_processing || {};
        document.getElementById('proc-sku-prefix').value = dataProc.remove_sku_prefix || '';
        document.getElementById('proc-phone-prefix').value = dataProc.remove_phone_prefix || '';
        document.getElementById('proc-building').value = dataProc.default_building_number || '';
        document.getElementById('proc-skip-b2b').value = (dataProc.skip_b2b_number_values || []).join(', ');

        // Advanced options
        const options = config.options || {};
        document.getElementById('opt-auto-detect').checked = options.auto_detect_chrome_host !== false;
        document.getElementById('opt-use-js').checked = options.use_javascript_for_form_filling !== false;
        document.getElementById('opt-preserve-polish').checked = options.preserve_polish_characters !== false;
        document.getElementById('log-level').value = options.log_level || 'INFO';

        // Helper service
        const helper = config.helper_service || {};
        document.getElementById('helper-default-url').value = helper.default_url || '';
        document.getElementById('helper-docker-url').value = helper.docker_url || '';

    } catch (error) {
        console.error('Failed to load configuration:', error);
    }
}

// Save configuration
document.getElementById('save-config-btn').addEventListener('click', async () => {
    const config = {
        // General
        chrome_path: document.getElementById('chrome-path').value,
        chrome_user_data_dir: document.getElementById('user-data-dir').value,
        chrome_debug_port: parseInt(document.getElementById('debug-port').value),
        baselinker_url: document.getElementById('baselinker-url').value,
        b2b_hendi_url: document.getElementById('b2b-url').value,
        baselinker_keywords: document.getElementById('baselinker-keywords').value.split(',').map(s => s.trim()).filter(s => s),
        b2b_keywords: document.getElementById('b2b-keywords').value.split(',').map(s => s.trim()).filter(s => s),

        // BaseLinker selectors
        baselinker_selectors: {
            products_container: document.getElementById('bl-products-container').value,
            total_price: document.getElementById('bl-total-price').value,
            paid_amount: document.getElementById('bl-paid-amount').value,
            phone: document.getElementById('bl-phone').value,
            email: document.getElementById('bl-email').value,
            b2b_number_field: document.getElementById('bl-b2b-field').value,
            address: {
                fullname: document.getElementById('bl-addr-fullname').value,
                company: document.getElementById('bl-addr-company').value,
                street: document.getElementById('bl-addr-street').value,
                city: document.getElementById('bl-addr-city').value,
                postcode: document.getElementById('bl-addr-postcode').value
            }
        },

        // Regex patterns
        regex_patterns: {
            baselinker: {
                sku: document.getElementById('bl-regex-sku').value,
                quantity: document.getElementById('bl-regex-quantity').value,
                price_amount: document.getElementById('bl-regex-price').value
            },
            b2b: {
                order_number: document.getElementById('b2b-regex-order').value
            }
        },

        // B2B selectors
        b2b_selectors: {
            order_settings_container: document.getElementById('b2b-order-container').value,
            import_button: document.getElementById('b2b-import-btn').value,
            import_modal: document.getElementById('b2b-import-modal').value,
            file_input: document.getElementById('b2b-file-input').value,
            continue_button: document.getElementById('b2b-continue-btn').value,
            add_to_cart_button: document.getElementById('b2b-add-cart-btn').value,
            checkout_button: document.getElementById('b2b-checkout-btn').value,
            new_address_checkbox: 'new_delivery_address',
            address_modal: '.jsAddAddressModal',
            save_address_button: 'button[type="submit"][form="user-address-form"]',
            address_form_fields: {
                name: 'address_data[name]',
                phone: 'address_data[phone]',
                email: 'address_data[email]',
                street: 'address_data[street]',
                street_no: 'address_data[street_no]',
                street_flat: 'address_data[street_flat]',
                zip: 'address_data[zip]',
                city: 'address_data[city]'
            },
            payment: {
                bank_transfer_radio: `input[type="radio"][name="payment_id"][value="${document.getElementById('b2b-payment-transfer').value}"]`,
                cash_on_delivery_radio: `input[type="radio"][name="payment_id"][value="${document.getElementById('b2b-payment-cash').value}"]`,
                cash_amount_field: `payment_params[custom_payment_price][${document.getElementById('b2b-payment-cash').value}]`,
                bank_transfer_label: `label[for="${document.getElementById('b2b-payment-transfer').value}"]`,
                cash_on_delivery_label: `label[for="${document.getElementById('b2b-payment-cash').value}"]`
            }
        },

        // Payment methods
        payment_methods: {
            bank_transfer_value: document.getElementById('b2b-payment-transfer').value,
            cash_on_delivery_value: document.getElementById('b2b-payment-cash').value
        },

        // CSV config
        csv_config: {
            delimiter: document.getElementById('csv-delimiter').value,
            encoding: document.getElementById('csv-encoding').value,
            headers: document.getElementById('csv-headers').value.split(',').map(s => s.trim()).filter(s => s)
        },

        // Timing
        timing: {
            default_timeout: parseFloat(document.getElementById('timing-default').value),
            element_wait_timeout: parseFloat(document.getElementById('timing-element').value),
            after_click_delay: parseFloat(document.getElementById('timing-click').value),
            after_file_upload_delay: parseFloat(document.getElementById('timing-upload').value),
            between_steps_delay: parseFloat(document.getElementById('timing-steps').value),
            chrome_startup_delay: parseFloat(document.getElementById('timing-startup').value),
            modal_open_delay: parseFloat(document.getElementById('timing-modal').value),
            form_submit_delay: parseFloat(document.getElementById('timing-form').value),
            payment_section_delay: parseFloat(document.getElementById('timing-payment').value)
        },

        // Data processing
        data_processing: {
            remove_sku_prefix: document.getElementById('proc-sku-prefix').value,
            remove_phone_prefix: document.getElementById('proc-phone-prefix').value,
            default_building_number: document.getElementById('proc-building').value,
            skip_b2b_number_values: document.getElementById('proc-skip-b2b').value.split(',').map(s => s.trim()).filter(s => s)
        },

        // Helper service
        helper_service: {
            default_url: document.getElementById('helper-default-url').value,
            docker_url: document.getElementById('helper-docker-url').value
        },

        // Options
        options: {
            auto_detect_chrome_host: document.getElementById('opt-auto-detect').checked,
            use_javascript_for_form_filling: document.getElementById('opt-use-js').checked,
            preserve_polish_characters: document.getElementById('opt-preserve-polish').checked,
            log_level: document.getElementById('log-level').value
        }
    };

    try {
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });

        const result = await response.json();
        if (result.success) {
            alert('Configuration saved successfully!');
            document.getElementById('config-section').style.display = 'none';
        } else {
            alert('Failed to save configuration: ' + result.error);
        }
    } catch (error) {
        console.error('Failed to save configuration:', error);
        alert('Failed to save configuration: ' + error.message);
    }
});

// Update status
async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();

        const chromeStatus = document.getElementById('chrome-status');
        const chromeText = document.getElementById('chrome-status-text');
        if (status.chrome_running) {
            chromeStatus.className = 'status-indicator status-ok';
            chromeText.textContent = 'Running';
        } else {
            chromeStatus.className = 'status-indicator status-error';
            chromeText.textContent = 'Not running';
        }

        document.getElementById('system-info').textContent = `System: ${status.system}`;

        const baselinkerStatus = document.getElementById('baselinker-status');
        const baselinkerText = document.getElementById('baselinker-status-text');
        if (status.baselinker_open) {
            baselinkerStatus.className = 'status-indicator status-ok';
            baselinkerText.textContent = 'Open';
            document.getElementById('baselinker-title').textContent = status.baselinker_title || '';
        } else {
            baselinkerStatus.className = 'status-indicator status-error';
            baselinkerText.textContent = 'Not found';
            document.getElementById('baselinker-title').textContent = '';
        }

        const b2bStatus = document.getElementById('b2b-status');
        const b2bText = document.getElementById('b2b-status-text');
        if (status.b2b_hendi_open) {
            b2bStatus.className = 'status-indicator status-ok';
            b2bText.textContent = 'Open';
            document.getElementById('b2b-title').textContent = status.b2b_hendi_title || '';
        } else {
            b2bStatus.className = 'status-indicator status-error';
            b2bText.textContent = 'Not found';
            document.getElementById('b2b-title').textContent = '';
        }
    } catch (error) {
        console.error('Failed to update status:', error);
    }
}

// Launch Chrome
document.getElementById('launch-chrome-btn').addEventListener('click', async () => {
    try {
        const response = await fetch('/api/launch-chrome', {
            method: 'POST'
        });
        const result = await response.json();

        if (result.success) {
            setTimeout(updateStatus, 2000);
        }
    } catch (error) {
        console.error('Failed to launch Chrome:', error);
    }
});

// Refresh status
document.getElementById('refresh-status-btn').addEventListener('click', () => {
    updateStatus();
});

// Toggle configuration
document.getElementById('config-btn').addEventListener('click', () => {
    const configSection = document.getElementById('config-section');
    if (configSection.style.display === 'none') {
        configSection.style.display = 'block';
        loadConfig();
    } else {
        configSection.style.display = 'none';
    }
});

document.getElementById('cancel-config-btn').addEventListener('click', () => {
    document.getElementById('config-section').style.display = 'none';
});

// Extract Order Data
document.getElementById('extract-order-btn').addEventListener('click', async () => {
    try {
        const response = await fetch('/api/extract-order', {
            method: 'POST'
        });
        const result = await response.json();

        if (result.success) {
            displayOrderData(result);
            document.getElementById('order-data-section').style.display = 'block';
        }
    } catch (error) {
        console.error('Failed to extract order data:', error);
    }
});

// Extract & Import to B2B
document.getElementById('extract-and-import-btn').addEventListener('click', async () => {
    try {
        const extractResponse = await fetch('/api/extract-order', {
            method: 'POST'
        });
        const extractResult = await extractResponse.json();

        if (!extractResult.success) {
            return;
        }

        const products = extractResult.products || [];
        const address = {
            company: extractResult.address?.company || '',
            phone: extractResult.phone || '',
            address: extractResult.address?.address || '',
            city: extractResult.address?.city || '',
            postal_code: extractResult.address?.postal_code || ''
        };
        const email = extractResult.email || '';
        const payment_amount = extractResult.payment_amount || '0';

        if (products.length === 0 || !address.company || !address.phone || !email) {
            return;
        }

        await fetch('/api/complete-order', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                products: products,
                address: address,
                email: email,
                payment_amount: payment_amount
            })
        });

    } catch (error) {
        console.error('Failed to extract and import:', error);
    }
});

// Display order data
function displayOrderData(data) {
    const tbody = document.getElementById('products-tbody');
    tbody.innerHTML = '';
    
    if (data.products && data.products.length > 0) {
        data.products.forEach(product => {
            addProductRow(product.sku, product.quantity);
        });
    }

    document.getElementById('order-phone').value = data.phone || '';
    document.getElementById('order-email').value = data.email || '';
    document.getElementById('order-payment').value = data.payment_amount || '';

    if (data.address) {
        document.getElementById('order-name').value = data.address.name || '';
        document.getElementById('order-company').value = data.address.company || '';
        document.getElementById('order-address').value = data.address.address || '';
        document.getElementById('order-city').value = data.address.city || '';
        document.getElementById('order-postal-code').value = data.address.postal_code || '';
    }
}

// Add product row
function addProductRow(sku = '', quantity = '') {
    const tbody = document.getElementById('products-tbody');
    const row = tbody.insertRow();
    
    row.innerHTML = `
        <td><input type="text" class="form-control form-control-sm product-sku" value="${sku}"></td>
        <td><input type="number" class="form-control form-control-sm product-quantity" value="${quantity}"></td>
        <td><button class="btn btn-sm btn-danger remove-product-btn"><i class="bi bi-trash"></i></button></td>
    `;

    row.querySelector('.remove-product-btn').addEventListener('click', () => {
        row.remove();
    });
}

// Add product button
document.getElementById('add-product-btn').addEventListener('click', () => {
    addProductRow();
});

// Close order data
document.getElementById('close-order-data-btn').addEventListener('click', () => {
    document.getElementById('order-data-section').style.display = 'none';
});

// Clear order data
document.getElementById('clear-order-btn').addEventListener('click', () => {
    if (confirm('Are you sure you want to clear all order data?')) {
        document.getElementById('products-tbody').innerHTML = '';
        document.getElementById('order-phone').value = '';
        document.getElementById('order-email').value = '';
        document.getElementById('order-payment').value = '';
        document.getElementById('order-name').value = '';
        document.getElementById('order-company').value = '';
        document.getElementById('order-address').value = '';
        document.getElementById('order-city').value = '';
        document.getElementById('order-postal-code').value = '';
    }
});

// Import to B2B
document.getElementById('import-to-b2b-btn').addEventListener('click', async () => {
    const products = [];
    document.querySelectorAll('#products-tbody tr').forEach(row => {
        const sku = row.querySelector('.product-sku').value;
        const quantity = row.querySelector('.product-quantity').value;
        if (sku && quantity) {
            products.push({ sku, quantity });
        }
    });

    if (products.length === 0) {
        alert('No products to import');
        return;
    }

    const address = {
        company: document.getElementById('order-company').value,
        phone: document.getElementById('order-phone').value,
        address: document.getElementById('order-address').value,
        city: document.getElementById('order-city').value,
        postal_code: document.getElementById('order-postal-code').value
    };

    const email = document.getElementById('order-email').value;
    const payment_amount = document.getElementById('order-payment').value;

    if (!address.company || !address.phone || !email || !address.address || !address.city || !address.postal_code) {
        alert('Please fill all address fields');
        return;
    }
    
    try {
        await fetch('/api/complete-order', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                products: products,
                address: address,
                email: email,
                payment_amount: payment_amount
            })
        });
    } catch (error) {
        console.error('Failed to complete order:', error);
    }
});

// Auto-refresh
statusInterval = setInterval(updateStatus, 5000);
logsInterval = setInterval(updateLogs, 2000);

// Initial updates
updateStatus();
updateLogs();