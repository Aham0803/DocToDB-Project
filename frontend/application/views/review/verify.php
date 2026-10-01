<div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-2 mb-3">
    <div>
        <h4 class="fw-bold mb-1">
            <i class="bi bi-shield-check text-primary me-2"></i> Human-in-the-Loop Verification Workspace
        </h4>
        <small class="text-secondary">
            Document ID: <code class="text-info"><?php echo htmlspecialchars($document['id']); ?></code> &bull; 
            File: <strong><?php echo htmlspecialchars($document['original_filename']); ?></strong> &bull; 
            LangGraph Confidence: <span class="badge bg-warning text-dark"><?php echo round($document['composite_confidence'] * 100, 1); ?>%</span>
        </small>
    </div>
    <div class="d-flex gap-2">
        <a href="<?php echo base_url('queue'); ?>" class="btn btn-sm btn-outline-secondary">
            <i class="bi bi-arrow-left me-1"></i> Back to Queue
        </a>
    </div>
</div>

<!-- Alert Banner: Flagged Reasons & Issues -->
<?php if (!empty($flags)): ?>
    <div class="flag-alert danger mb-3">
        <div class="d-flex align-items-start gap-2">
            <i class="bi bi-exclamation-octagon-fill fs-5 text-danger mt-1"></i>
            <div>
                <strong class="d-block mb-1">Validation & GST Rule Diagnostics Detected:</strong>
                <ul class="mb-0 ps-3 small">
                    <?php foreach ($flags as $flag): ?>
                        <li><?php echo htmlspecialchars($flag); ?></li>
                    <?php endforeach; ?>
                </ul>
            </div>
        </div>
    </div>
<?php endif; ?>

<!-- Submission Feedback Alert -->
<div id="reviewAlertBox" class="alert d-none mb-3" role="alert"></div>

<!-- Split Screen Layout -->
<div class="row g-3">
    <!-- LEFT COLUMN: Document Viewer Pane -->
    <div class="col-lg-6">
        <div class="doc-viewer-pane">
            <div class="p-2 px-3 bg-dark border-bottom border-secondary border-opacity-25 d-flex justify-content-between align-items-center">
                <span class="small fw-semibold text-light">
                    <i class="bi bi-eye-fill me-1 text-primary"></i> Source Document Preview
                </span>
                <div class="d-flex gap-2">
                    <a href="<?php echo $file_url; ?>" target="_blank" class="btn btn-xs btn-outline-info text-decoration-none">
                        <i class="bi bi-box-arrow-up-right me-1"></i> Open Raw
                    </a>
                </div>
            </div>

            <div class="flex-grow-1 position-relative">
                <?php if (strpos($document['file_type'], 'pdf') !== false): ?>
                    <embed src="<?php echo $file_url; ?>" type="application/pdf" class="doc-viewer-frame">
                <?php else: ?>
                    <div class="p-3 text-center h-100 overflow-auto">
                        <img src="<?php echo $file_url; ?>" alt="Invoice Image" class="img-fluid rounded border border-secondary border-opacity-25">
                    </div>
                <?php endif; ?>
            </div>
        </div>
    </div>

    <!-- RIGHT COLUMN: Editable Structured GST Form -->
    <div class="col-lg-6">
        <div class="glass-card doc-edit-pane">
            <form id="hitlReviewForm" data-doc-id="<?php echo $document['id']; ?>" action="<?php echo base_url('review/submit/' . $document['id']); ?>">
                
                <!-- Section 1: Invoice Header -->
                <div class="border-bottom border-secondary border-opacity-25 pb-3 mb-3">
                    <h6 class="fw-bold text-light mb-2"><i class="bi bi-receipt me-1 text-primary"></i> 1. Invoice Metadata</h6>
                    <div class="row g-2">
                        <div class="col-sm-6">
                            <label class="form-label small text-secondary mb-1">Invoice Number *</label>
                            <input type="text" id="invoice_number" class="form-control form-control-sm bg-dark text-light border-secondary" 
                                value="<?php echo htmlspecialchars(isset($extracted['invoice_number']) ? $extracted['invoice_number'] : ''); ?>" required>
                        </div>
                        <div class="col-sm-3">
                            <label class="form-label small text-secondary mb-1">Invoice Date *</label>
                            <input type="date" id="invoice_date" class="form-control form-control-sm bg-dark text-light border-secondary" 
                                value="<?php echo htmlspecialchars(isset($extracted['invoice_date']) ? $extracted['invoice_date'] : date('Y-m-d')); ?>" required>
                        </div>
                        <div class="col-sm-3">
                            <label class="form-label small text-secondary mb-1">Due Date</label>
                            <input type="date" id="due_date" class="form-control form-control-sm bg-dark text-light border-secondary" 
                                value="<?php echo htmlspecialchars(isset($extracted['due_date']) ? $extracted['due_date'] : ''); ?>">
                        </div>
                        <div class="col-sm-6">
                            <label class="form-label small text-secondary mb-1">PO Number</label>
                            <input type="text" id="purchase_order_number" class="form-control form-control-sm bg-dark text-light border-secondary" 
                                value="<?php echo htmlspecialchars(isset($extracted['purchase_order_number']) ? $extracted['purchase_order_number'] : ''); ?>">
                        </div>
                        <div class="col-sm-6">
                            <label class="form-label small text-secondary mb-1">Currency</label>
                            <input type="text" id="currency" class="form-control form-control-sm bg-dark text-light border-secondary" 
                                value="<?php echo htmlspecialchars(isset($extracted['currency']) ? $extracted['currency'] : 'INR'); ?>">
                        </div>
                    </div>
                </div>

                <!-- Section 2: Vendor Details -->
                <div class="border-bottom border-secondary border-opacity-25 pb-3 mb-3">
                    <h6 class="fw-bold text-light mb-2"><i class="bi bi-building me-1 text-warning"></i> 2. Vendor / Supplier (GSTIN Checksum Anchor)</h6>
                    <div class="row g-2">
                        <div class="col-sm-7">
                            <label class="form-label small text-secondary mb-1">Vendor Trade / Legal Name *</label>
                            <input type="text" id="vendor_name" class="form-control form-control-sm bg-dark text-light border-secondary" 
                                value="<?php echo htmlspecialchars(isset($extracted['vendor_name']) ? $extracted['vendor_name'] : ''); ?>" required>
                        </div>
                        <div class="col-sm-5">
                            <label class="form-label small text-secondary mb-1">Vendor GSTIN (15 Chars) *</label>
                            <input type="text" id="vendor_gstin" maxlength="15" class="form-control form-control-sm bg-dark text-light border-secondary font-mono" 
                                value="<?php echo htmlspecialchars(isset($extracted['vendor_gstin']) ? $extracted['vendor_gstin'] : ''); ?>" required>
                        </div>
                        <div class="col-sm-12">
                            <label class="form-label small text-secondary mb-1">Vendor Address</label>
                            <input type="text" id="vendor_address" class="form-control form-control-sm bg-dark text-light border-secondary" 
                                value="<?php echo htmlspecialchars(isset($extracted['vendor_address']) ? $extracted['vendor_address'] : ''); ?>">
                        </div>
                        <div class="col-sm-4">
                            <label class="form-label small text-secondary mb-1">Vendor PAN</label>
                            <input type="text" id="vendor_pan" maxlength="10" class="form-control form-control-sm bg-dark text-light border-secondary font-mono" 
                                value="<?php echo htmlspecialchars(isset($extracted['vendor_pan']) ? $extracted['vendor_pan'] : ''); ?>">
                        </div>
                        <div class="col-sm-4">
                            <label class="form-label small text-secondary mb-1">Phone</label>
                            <input type="text" id="vendor_phone" class="form-control form-control-sm bg-dark text-light border-secondary" 
                                value="<?php echo htmlspecialchars(isset($extracted['vendor_phone']) ? $extracted['vendor_phone'] : ''); ?>">
                        </div>
                        <div class="col-sm-4">
                            <label class="form-label small text-secondary mb-1">Email</label>
                            <input type="email" id="vendor_email" class="form-control form-control-sm bg-dark text-light border-secondary" 
                                value="<?php echo htmlspecialchars(isset($extracted['vendor_email']) ? $extracted['vendor_email'] : ''); ?>">
                        </div>
                    </div>
                </div>

                <!-- Section 3: Customer & Place of Supply (POS) -->
                <div class="border-bottom border-secondary border-opacity-25 pb-3 mb-3">
                    <h6 class="fw-bold text-light mb-2"><i class="bi bi-person-badge me-1 text-info"></i> 3. Customer & Place of Supply (POS)</h6>
                    <div class="row g-2">
                        <div class="col-sm-7">
                            <label class="form-label small text-secondary mb-1">Customer / Buyer Name *</label>
                            <input type="text" id="customer_name" class="form-control form-control-sm bg-dark text-light border-secondary" 
                                value="<?php echo htmlspecialchars(isset($extracted['customer_name']) ? $extracted['customer_name'] : ''); ?>" required>
                        </div>
                        <div class="col-sm-5">
                            <label class="form-label small text-secondary mb-1">Customer GSTIN</label>
                            <input type="text" id="customer_gstin" maxlength="15" class="form-control form-control-sm bg-dark text-light border-secondary font-mono" 
                                value="<?php echo htmlspecialchars(isset($extracted['customer_gstin']) ? $extracted['customer_gstin'] : ''); ?>">
                        </div>
                        <div class="col-sm-6">
                            <label class="form-label small text-secondary mb-1">Place of Supply (State / Code)</label>
                            <input type="text" id="place_of_supply" class="form-control form-control-sm bg-dark text-light border-secondary" 
                                value="<?php echo htmlspecialchars(isset($extracted['place_of_supply']) ? $extracted['place_of_supply'] : ''); ?>">
                        </div>
                        <div class="col-sm-6 d-flex align-items-center gap-3 pt-3">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="is_interstate" <?php echo (!empty($extracted['is_interstate'])) ? 'checked' : ''; ?>>
                                <label class="form-check-label small text-light" for="is_interstate">
                                    Inter-State (IGST)
                                </label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="reverse_charge" <?php echo (!empty($extracted['reverse_charge'])) ? 'checked' : ''; ?>>
                                <label class="form-check-label small text-light" for="reverse_charge">
                                    Reverse Charge (RCM)
                                </label>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Section 4: Line Items Table -->
                <div class="border-bottom border-secondary border-opacity-25 pb-3 mb-3">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <h6 class="fw-bold text-light mb-0"><i class="bi bi-list-check me-1 text-success"></i> 4. Line Items & Tax Slabs</h6>
                    </div>

                    <div class="table-responsive">
                        <table class="table table-sm table-custom" id="itemsTable">
                            <thead>
                                <tr>
                                    <th>Description</th>
                                    <th style="width: 80px;">HSN</th>
                                    <th style="width: 70px;">Qty</th>
                                    <th style="width: 100px;">Unit Price</th>
                                    <th style="width: 100px;">Taxable</th>
                                    <th style="width: 80px;">GST %</th>
                                    <th style="width: 100px;">Total</th>
                                </tr>
                            </thead>
                            <tbody id="lineItemsBody">
                                <?php 
                                    $items = isset($extracted['items']) && is_array($extracted['items']) ? $extracted['items'] : array();
                                    if (empty($items)) {
                                        $items = array(array('description' => 'Item 1', 'hsn_sac_code' => '998311', 'quantity' => 1, 'unit_price' => 0, 'tax_rate' => 18, 'total_amount' => 0));
                                    }
                                    foreach ($items as $it): 
                                ?>
                                    <tr class="line-item-row">
                                        <td>
                                            <input type="text" class="form-control form-control-sm bg-dark text-light border-secondary item-desc" 
                                                value="<?php echo htmlspecialchars(isset($it['description']) ? $it['description'] : ''); ?>">
                                        </td>
                                        <td>
                                            <input type="text" class="form-control form-control-sm bg-dark text-light border-secondary item-hsn font-mono" 
                                                value="<?php echo htmlspecialchars(isset($it['hsn_sac_code']) ? $it['hsn_sac_code'] : ''); ?>">
                                        </td>
                                        <td>
                                            <input type="number" step="any" class="form-control form-control-sm bg-dark text-light border-secondary item-qty" 
                                                value="<?php echo isset($it['quantity']) ? $it['quantity'] : 1; ?>">
                                        </td>
                                        <td>
                                            <input type="number" step="0.01" class="form-control form-control-sm bg-dark text-light border-secondary item-price" 
                                                value="<?php echo isset($it['unit_price']) ? $it['unit_price'] : 0; ?>">
                                        </td>
                                        <td>
                                            <input type="number" step="0.01" class="form-control form-control-sm bg-dark text-light border-secondary item-taxable" 
                                                value="<?php echo isset($it['taxable_value']) ? $it['taxable_value'] : 0; ?>">
                                        </td>
                                        <td>
                                            <select class="form-select form-select-sm bg-dark text-light border-secondary item-tax-rate">
                                                <?php 
                                                    $curr_rate = isset($it['tax_rate']) ? floatval($it['tax_rate']) : 18.0;
                                                    foreach (array(0, 5, 12, 18, 28) as $slab):
                                                ?>
                                                    <option value="<?php echo $slab; ?>" <?php echo (abs($curr_rate - $slab) < 0.2) ? 'selected' : ''; ?>>
                                                        <?php echo $slab; ?>%
                                                    </option>
                                                <?php endforeach; ?>
                                            </select>
                                        </td>
                                        <td>
                                            <input type="number" step="0.01" class="form-control form-control-sm bg-dark text-light border-secondary item-total-amount" 
                                                value="<?php echo isset($it['total_amount']) ? $it['total_amount'] : 0; ?>">
                                        </td>
                                    </tr>
                                <?php endforeach; ?>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Section 5: Financial Reconciliation Totals -->
                <div class="p-3 rounded-3 bg-dark bg-opacity-50 border border-secondary border-opacity-25 mb-3">
                    <h6 class="fw-bold text-light mb-2"><i class="bi bi-calculator me-1 text-info"></i> 5. Mathematical Totals & Tax Split</h6>
                    <div class="row g-2">
                        <div class="col-sm-4">
                            <label class="form-label small text-secondary mb-1">Subtotal Amount (₹)</label>
                            <input type="number" step="0.01" id="subtotal_amount" class="form-control form-control-sm bg-dark text-light border-secondary" 
                                value="<?php echo isset($extracted['subtotal_amount']) ? $extracted['subtotal_amount'] : 0; ?>">
                        </div>
                        <div class="col-sm-4">
                            <label class="form-label small text-secondary mb-1">CGST (₹)</label>
                            <input type="number" step="0.01" id="cgst_amount" class="form-control form-control-sm bg-dark text-light border-secondary" 
                                value="<?php echo isset($extracted['cgst_amount']) ? $extracted['cgst_amount'] : 0; ?>">
                        </div>
                        <div class="col-sm-4">
                            <label class="form-label small text-secondary mb-1">SGST (₹)</label>
                            <input type="number" step="0.01" id="sgst_amount" class="form-control form-control-sm bg-dark text-light border-secondary" 
                                value="<?php echo isset($extracted['sgst_amount']) ? $extracted['sgst_amount'] : 0; ?>">
                        </div>
                        <div class="col-sm-4">
                            <label class="form-label small text-secondary mb-1">IGST (₹)</label>
                            <input type="number" step="0.01" id="igst_amount" class="form-control form-control-sm bg-dark text-light border-secondary" 
                                value="<?php echo isset($extracted['igst_amount']) ? $extracted['igst_amount'] : 0; ?>">
                        </div>
                        <div class="col-sm-4">
                            <label class="form-label small text-secondary mb-1">Total Tax (₹)</label>
                            <input type="number" step="0.01" id="total_tax_amount" class="form-control form-control-sm bg-dark text-light border-secondary" 
                                value="<?php echo isset($extracted['total_tax_amount']) ? $extracted['total_tax_amount'] : 0; ?>">
                        </div>
                        <div class="col-sm-4">
                            <label class="form-label small text-secondary mb-1">Discount (₹)</label>
                            <input type="number" step="0.01" id="discount_amount" class="form-control form-control-sm bg-dark text-light border-secondary" 
                                value="<?php echo isset($extracted['discount_amount']) ? $extracted['discount_amount'] : 0; ?>">
                        </div>
                        <div class="col-sm-4">
                            <label class="form-label small text-secondary mb-1">Shipping / Freight (₹)</label>
                            <input type="number" step="0.01" id="shipping_amount" class="form-control form-control-sm bg-dark text-light border-secondary" 
                                value="<?php echo isset($extracted['shipping_amount']) ? $extracted['shipping_amount'] : 0; ?>">
                        </div>
                        <div class="col-sm-4">
                            <label class="form-label small text-secondary mb-1">Round Off (₹)</label>
                            <input type="number" step="0.01" id="round_off_amount" class="form-control form-control-sm bg-dark text-light border-secondary" 
                                value="<?php echo isset($extracted['round_off_amount']) ? $extracted['round_off_amount'] : 0; ?>">
                        </div>
                        <div class="col-sm-4">
                            <label class="form-label small fw-bold text-success mb-1">Grand Total (₹) *</label>
                            <input type="number" step="0.01" id="grand_total" class="form-control form-control-sm bg-dark text-success fw-bold border-success" 
                                value="<?php echo isset($extracted['grand_total']) ? $extracted['grand_total'] : 0; ?>" required>
                        </div>
                    </div>
                </div>

                <!-- Section 6: Bank & Payment Terms -->
                <div class="border-bottom border-secondary border-opacity-25 pb-3 mb-3">
                    <h6 class="fw-bold text-light mb-2"><i class="bi bi-bank me-1 text-secondary"></i> 6. Bank Details & Terms</h6>
                    <div class="row g-2">
                        <div class="col-sm-4">
                            <label class="form-label small text-secondary mb-1">Bank Name</label>
                            <input type="text" id="bank_name" class="form-control form-control-sm bg-dark text-light border-secondary" 
                                value="<?php echo htmlspecialchars(isset($extracted['bank_name']) ? $extracted['bank_name'] : ''); ?>">
                        </div>
                        <div class="col-sm-4">
                            <label class="form-label small text-secondary mb-1">Account Number</label>
                            <input type="text" id="account_number" class="form-control form-control-sm bg-dark text-light border-secondary font-mono" 
                                value="<?php echo htmlspecialchars(isset($extracted['account_number']) ? $extracted['account_number'] : ''); ?>">
                        </div>
                        <div class="col-sm-4">
                            <label class="form-label small text-secondary mb-1">IFSC Code</label>
                            <input type="text" id="ifsc_code" class="form-control form-control-sm bg-dark text-light border-secondary font-mono" 
                                value="<?php echo htmlspecialchars(isset($extracted['ifsc_code']) ? $extracted['ifsc_code'] : ''); ?>">
                        </div>
                        <div class="col-sm-12">
                            <label class="form-label small text-secondary mb-1">Payment Terms</label>
                            <input type="text" id="payment_terms" class="form-control form-control-sm bg-dark text-light border-secondary" 
                                value="<?php echo htmlspecialchars(isset($extracted['payment_terms']) ? $extracted['payment_terms'] : ''); ?>">
                        </div>
                    </div>
                </div>

                <!-- Action CTA Bar -->
                <div class="d-flex justify-content-between align-items-center pt-2">
                    <small class="text-muted">
                        <i class="bi bi-database-add me-1"></i> Saving captures diffs in <code>human_corrections</code> table.
                    </small>
                    <div class="d-flex gap-2">
                        <button type="submit" id="submitReviewBtn" class="btn btn-success">
                            <i class="bi bi-check2-circle me-1"></i> Approve & Save to MySQL
                        </button>
                    </div>
                </div>

            </form>
        </div>
    </div>
</div>
