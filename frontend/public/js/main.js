// ========================================================
// DocToDB Frontend Interactions & State Handlers
// ========================================================

document.addEventListener('DOMContentLoaded', function () {
    initDropzone();
    initReviewFormMath();
    initChatInterface();
});

/**
 * 1. Drag & Drop File Upload Handler
 */
function initDropzone() {
    const dropzone = document.getElementById('invoiceDropzone');
    const fileInput = document.getElementById('invoiceFileInput');
    const uploadProgress = document.getElementById('uploadProgress');
    const progressBar = document.getElementById('progressBar');
    const uploadStatusText = document.getElementById('uploadStatusText');

    if (!dropzone || !fileInput) return;

    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('dragover');
        }, false);
    });

    dropzone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });

    function handleFileUpload(file) {
        const providerSelect = document.getElementById('providerSelect');
        const provider = providerSelect ? providerSelect.value : null;

        const formData = new FormData();
        formData.append('file', file);
        if (provider) formData.append('provider', provider);

        uploadProgress.classList.remove('d-none');
        dropzone.classList.add('opacity-50', 'pe-none');
        progressBar.style.width = '35%';
        uploadStatusText.innerHTML = '<i class="bi bi-gear-wide-connected spin me-1"></i> Running LangGraph Agent: Parsing Document & Extracting GST Data...';

        fetch(window.UPLOAD_AJAX_URL || '/upload/ajax', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            progressBar.style.width = '100%';
            if (data.success) {
                uploadStatusText.innerHTML = `<span class="text-success"><i class="bi bi-check-circle-fill me-1"></i> Completed! Status: <strong>${data.status}</strong>. Redirecting...</span>`;
                setTimeout(() => {
                    window.location.href = data.redirect_url;
                }, 1200);
            } else {
                uploadStatusText.innerHTML = `<span class="text-danger"><i class="bi bi-x-circle-fill me-1"></i> Error: ${data.message}</span>`;
                dropzone.classList.remove('opacity-50', 'pe-none');
            }
        })
        .catch(err => {
            uploadStatusText.innerHTML = `<span class="text-danger"><i class="bi bi-exclamation-triangle-fill me-1"></i> Upload failed: ${err.message}</span>`;
            dropzone.classList.remove('opacity-50', 'pe-none');
        });
    }
}

/**
 * 2. HITL Review Form Dynamic Math Recalculation
 */
function initReviewFormMath() {
    const reviewForm = document.getElementById('hitlReviewForm');
    if (!reviewForm) return;

    // Line item recalculation
    function recalculateTotals() {
        let subtotal = 0;
        let totalCGST = 0;
        let totalSGST = 0;
        let totalIGST = 0;

        const itemRows = document.querySelectorAll('.line-item-row');
        itemRows.forEach(row => {
            const qty = parseFloat(row.querySelector('.item-qty')?.value) || 0;
            const price = parseFloat(row.querySelector('.item-price')?.value) || 0;
            const taxable = qty * price;
            
            const taxableInput = row.querySelector('.item-taxable');
            if (taxableInput) taxableInput.value = taxable.toFixed(2);

            const taxRate = parseFloat(row.querySelector('.item-tax-rate')?.value) || 0;
            const isInterstate = document.getElementById('is_interstate')?.checked;

            let itemTax = (taxable * taxRate) / 100;
            if (isInterstate) {
                totalIGST += itemTax;
            } else {
                totalCGST += (itemTax / 2);
                totalSGST += (itemTax / 2);
            }

            subtotal += taxable;
            const totalItemAmount = row.querySelector('.item-total-amount');
            if (totalItemAmount) totalItemAmount.value = (taxable + itemTax).toFixed(2);
        });

        // Update Totals Fields
        const subtotalInput = document.getElementById('subtotal_amount');
        if (subtotalInput) subtotalInput.value = subtotal.toFixed(2);

        const cgstInput = document.getElementById('cgst_amount');
        if (cgstInput) cgstInput.value = totalCGST.toFixed(2);

        const sgstInput = document.getElementById('sgst_amount');
        if (sgstInput) sgstInput.value = totalSGST.toFixed(2);

        const igstInput = document.getElementById('igst_amount');
        if (igstInput) igstInput.value = totalIGST.toFixed(2);

        const totalTax = totalCGST + totalSGST + totalIGST;
        const totalTaxInput = document.getElementById('total_tax_amount');
        if (totalTaxInput) totalTaxInput.value = totalTax.toFixed(2);

        const discount = parseFloat(document.getElementById('discount_amount')?.value) || 0;
        const shipping = parseFloat(document.getElementById('shipping_amount')?.value) || 0;
        const roundOff = parseFloat(document.getElementById('round_off_amount')?.value) || 0;

        const grandTotal = subtotal + totalTax + shipping - discount + roundOff;
        const grandTotalInput = document.getElementById('grand_total');
        if (grandTotalInput) grandTotalInput.value = grandTotal.toFixed(2);
    }

    // Attach listener to inputs
    reviewForm.addEventListener('input', function (e) {
        if (e.target.matches('.item-qty, .item-price, .item-tax-rate, #discount_amount, #shipping_amount, #round_off_amount, #is_interstate')) {
            recalculateTotals();
        }
    });

    // Form Submission Handler
    reviewForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const submitBtn = document.getElementById('submitReviewBtn');
        const alertBox = document.getElementById('reviewAlertBox');

        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Committing to MySQL...';

        // Serialize Form into Structured Invoice JSON
        const items = [];
        document.querySelectorAll('.line-item-row').forEach((row, idx) => {
            items.push({
                item_index: idx + 1,
                description: row.querySelector('.item-desc')?.value || '',
                hsn_sac_code: row.querySelector('.item-hsn')?.value || '',
                quantity: parseFloat(row.querySelector('.item-qty')?.value) || 1,
                unit_of_measure: row.querySelector('.item-uom')?.value || 'NOS',
                unit_price: parseFloat(row.querySelector('.item-price')?.value) || 0,
                taxable_value: parseFloat(row.querySelector('.item-taxable')?.value) || 0,
                tax_rate: parseFloat(row.querySelector('.item-tax-rate')?.value) || 0,
                cgst_rate: (parseFloat(row.querySelector('.item-tax-rate')?.value) || 0) / 2,
                cgst_amount: 0,
                sgst_rate: (parseFloat(row.querySelector('.item-tax-rate')?.value) || 0) / 2,
                sgst_amount: 0,
                igst_rate: 0,
                igst_amount: 0,
                total_amount: parseFloat(row.querySelector('.item-total-amount')?.value) || 0
            });
        });

        const invoiceData = {
            invoice_number: document.getElementById('invoice_number').value,
            invoice_date: document.getElementById('invoice_date').value,
            due_date: document.getElementById('due_date').value || null,
            currency: document.getElementById('currency').value || 'INR',
            purchase_order_number: document.getElementById('purchase_order_number').value || null,
            vendor_name: document.getElementById('vendor_name').value,
            vendor_gstin: document.getElementById('vendor_gstin').value,
            vendor_address: document.getElementById('vendor_address').value || null,
            vendor_phone: document.getElementById('vendor_phone').value || null,
            vendor_email: document.getElementById('vendor_email').value || null,
            vendor_pan: document.getElementById('vendor_pan').value || null,
            customer_name: document.getElementById('customer_name').value,
            customer_gstin: document.getElementById('customer_gstin').value || null,
            place_of_supply: document.getElementById('place_of_supply').value || null,
            customer_address: document.getElementById('customer_address').value || null,
            subtotal_amount: parseFloat(document.getElementById('subtotal_amount').value) || 0,
            cgst_amount: parseFloat(document.getElementById('cgst_amount').value) || 0,
            sgst_amount: parseFloat(document.getElementById('sgst_amount').value) || 0,
            igst_amount: parseFloat(document.getElementById('igst_amount').value) || 0,
            total_tax_amount: parseFloat(document.getElementById('total_tax_amount').value) || 0,
            discount_amount: parseFloat(document.getElementById('discount_amount').value) || 0,
            shipping_amount: parseFloat(document.getElementById('shipping_amount').value) || 0,
            round_off_amount: parseFloat(document.getElementById('round_off_amount').value) || 0,
            grand_total: parseFloat(document.getElementById('grand_total').value) || 0,
            is_interstate: document.getElementById('is_interstate').checked,
            reverse_charge: document.getElementById('reverse_charge')?.checked || false,
            bank_name: document.getElementById('bank_name').value || null,
            account_number: document.getElementById('account_number').value || null,
            ifsc_code: document.getElementById('ifsc_code').value || null,
            payment_terms: document.getElementById('payment_terms').value || null,
            items: items
        };

        const docId = reviewForm.getAttribute('data-doc-id');
        const submitUrl = reviewForm.getAttribute('action');

        fetch(submitUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                reviewer_name: 'accounts_officer',
                corrected_data: invoiceData
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alertBox.classList.remove('d-none', 'alert-danger');
                alertBox.classList.add('alert-success');
                alertBox.innerHTML = `<i class="bi bi-check-circle-fill me-1"></i> ${data.message} Redirecting to verified invoices...`;
                setTimeout(() => {
                    window.location.href = data.redirect_url;
                }, 1200);
            } else {
                alertBox.classList.remove('d-none', 'alert-success');
                alertBox.classList.add('alert-danger');
                alertBox.innerHTML = `<i class="bi bi-x-circle-fill me-1"></i> ${data.message}`;
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="bi bi-check2-circle me-1"></i> Approve & Save to MySQL';
            }
        })
        .catch(err => {
            alertBox.classList.remove('d-none', 'alert-success');
            alertBox.classList.add('alert-danger');
            alertBox.innerHTML = `<i class="bi bi-exclamation-triangle-fill me-1"></i> Request failed: ${err.message}`;
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="bi bi-check2-circle me-1"></i> Approve & Save to MySQL';
        });
    });
}

/**
 * 3. Conversational RAG & Tool-Assisted Chat Interface
 */
function initChatInterface() {
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    const chatMessages = document.getElementById('chatMessages');

    if (!chatForm || !chatInput || !chatMessages) return;

    // Click on suggestion chip
    document.querySelectorAll('.suggestion-chip').forEach(chip => {
        chip.addEventListener('click', function () {
            chatInput.value = this.innerText.replace(/"/g, '');
            chatForm.dispatchEvent(new Event('submit'));
        });
    });

    chatForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const query = chatInput.value.trim();
        if (!query) return;

        // Append User Message
        appendMessage('user', query);
        chatInput.value = '';

        // Append Loading Bubble
        const loadingId = 'loading_' + Date.now();
        const loadingHtml = `
            <div id="${loadingId}" class="chat-bubble assistant">
                <span class="spinner-border spinner-border-sm text-primary me-2"></span>
                <span>Consulting Router (SQL Tools / ChromaDB RAG)...</span>
            </div>
        `;
        chatMessages.insertAdjacentHTML('beforeend', loadingHtml);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        fetch(window.CHAT_SEND_URL || '/chat/send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query })
        })
        .then(res => res.json())
        .then(res => {
            const loadingElem = document.getElementById(loadingId);
            if (loadingElem) loadingElem.remove();

            if (res.success && res.data) {
                appendAssistantMessage(res.data);
            } else {
                appendMessage('assistant', `<span class="text-danger">Error: ${res.message || 'Unable to process query.'}</span>`);
            }
        })
        .catch(err => {
            const loadingElem = document.getElementById(loadingId);
            if (loadingElem) loadingElem.remove();
            appendMessage('assistant', `<span class="text-danger">Network error: ${err.message}</span>`);
        });
    });

    function appendMessage(sender, text) {
        const bubble = document.createElement('div');
        bubble.className = `chat-bubble ${sender}`;
        bubble.innerHTML = text;
        chatMessages.appendChild(bubble);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function appendAssistantMessage(data) {
        const typeBadge = data.query_type === 'STRUCTURED_SQL_TOOL'
            ? `<span class="badge bg-success-subtle text-success border border-success-subtle mb-2"><i class="bi bi-database-check me-1"></i> Deterministic SQL Tool: <code>${data.tool_called}</code></span>`
            : `<span class="badge bg-primary-subtle text-primary border border-primary-subtle mb-2"><i class="bi bi-file-earmark-text me-1"></i> ChromaDB Vector RAG</span>`;

        let citationsHtml = '';
        if (data.citations && data.citations.length > 0) {
            citationsHtml = '<div class="mt-2 pt-2 border-top border-secondary border-opacity-25"><small class="text-muted d-block mb-1">Sources & Citations:</small>';
            data.citations.forEach(c => {
                const title = c.invoice_number ? `Invoice #${c.invoice_number}` : (c.vendor_name || 'Doc');
                citationsHtml += `<span class="citation-chip" title="${c.snippet || ''}"><i class="bi bi-link-45deg"></i> ${title}</span>`;
            });
            citationsHtml += '</div>';
        }

        const bubble = document.createElement('div');
        bubble.className = 'chat-bubble assistant';
        bubble.innerHTML = `
            ${typeBadge}
            <div class="message-content">${formatMarkdown(data.answer)}</div>
            ${citationsHtml}
        `;
        chatMessages.appendChild(bubble);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function formatMarkdown(text) {
        if (!text) return '';
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`([^`]+)`/g, '<code class="bg-dark px-1 rounded">$1</code>')
            .replace(/\n/g, '<br>');
    }
}
