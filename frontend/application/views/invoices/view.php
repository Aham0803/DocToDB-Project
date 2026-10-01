<div class="d-flex justify-content-between align-items-center mb-4">
    <div class="d-flex align-items-center gap-3">
        <a href="<?php echo base_url('invoices'); ?>" class="btn btn-sm btn-outline-secondary">
            <i class="bi bi-arrow-left me-1"></i> Back
        </a>
        <h4 class="fw-bold mb-0">
            Invoice #<?php echo htmlspecialchars($invoice['invoice_number']); ?>
        </h4>
        <span class="badge bg-success-subtle text-success border border-success-subtle">
            <?php echo htmlspecialchars($invoice['verification_type']); ?> APPROVED
        </span>
    </div>
    
    <div class="d-flex gap-2">
        <button onclick="window.print()" class="btn btn-sm btn-outline-info">
            <i class="bi bi-printer me-1"></i> Print Invoice
        </button>
    </div>
</div>

<div class="row g-4">
    <!-- Main Invoice Card -->
    <div class="col-lg-8">
        <div class="glass-card mb-4">
            <!-- Header Row -->
            <div class="d-flex justify-content-between align-items-start border-bottom border-secondary border-opacity-25 pb-4 mb-4">
                <div>
                    <h3 class="fw-bold text-light mb-1"><?php echo htmlspecialchars($invoice['vendor_name']); ?></h3>
                    <p class="text-secondary small mb-1"><?php echo nl2br(htmlspecialchars($invoice['vendor_address'] ?: '')); ?></p>
                    <div class="d-flex gap-3 small text-muted">
                        <span>GSTIN: <strong class="text-light font-mono"><?php echo htmlspecialchars($invoice['vendor_gstin']); ?></strong></span>
                        <?php if ($invoice['vendor_pan']): ?>
                            <span>PAN: <strong class="text-light font-mono"><?php echo htmlspecialchars($invoice['vendor_pan']); ?></strong></span>
                        <?php endif; ?>
                    </div>
                </div>

                <div class="text-end">
                    <span class="badge bg-primary text-uppercase px-2 py-1 mb-2">Tax Invoice</span>
                    <div class="fw-bold text-light fs-5">#<?php echo htmlspecialchars($invoice['invoice_number']); ?></div>
                    <small class="text-muted d-block">Invoice Date: <?php echo htmlspecialchars($invoice['invoice_date']); ?></small>
                    <?php if ($invoice['due_date']): ?>
                        <small class="text-warning d-block">Due Date: <?php echo htmlspecialchars($invoice['due_date']); ?></small>
                    <?php endif; ?>
                </div>
            </div>

            <!-- Buyer Details -->
            <div class="p-3 rounded-3 bg-dark bg-opacity-50 border border-secondary border-opacity-25 mb-4">
                <span class="text-secondary small text-uppercase fw-semibold d-block mb-1">Billed To (Customer):</span>
                <h5 class="fw-bold text-light mb-1"><?php echo htmlspecialchars($invoice['customer_name']); ?></h5>
                <p class="text-secondary small mb-1"><?php echo nl2br(htmlspecialchars($invoice['customer_address'] ?: '')); ?></p>
                <div class="d-flex gap-4 small text-muted">
                    <span>Customer GSTIN: <strong class="text-light font-mono"><?php echo htmlspecialchars($invoice['customer_gstin'] ?: 'B2C / Unregistered'); ?></strong></span>
                    <span>Place of Supply: <strong class="text-light"><?php echo htmlspecialchars($invoice['place_of_supply'] ?: 'Standard'); ?></strong></span>
                </div>
            </div>

            <!-- Line Items Table -->
            <h6 class="fw-bold text-light mb-3"><i class="bi bi-list-check me-2 text-primary"></i> Invoiced Items & Services</h6>
            <div class="table-responsive mb-4">
                <table class="table table-custom">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Description</th>
                            <th>HSN/SAC</th>
                            <th class="text-end">Qty</th>
                            <th class="text-end">Unit Price</th>
                            <th class="text-end">Taxable Val</th>
                            <th class="text-end">GST Rate</th>
                            <th class="text-end">Line Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($invoice['items'] as $item): ?>
                            <tr>
                                <td><?php echo $item['item_index']; ?></td>
                                <td class="fw-semibold text-light"><?php echo htmlspecialchars($item['description']); ?></td>
                                <td class="font-mono text-muted"><?php echo htmlspecialchars($item['hsn_sac_code'] ?: 'N/A'); ?></td>
                                <td class="text-end"><?php echo number_format($item['quantity'], 2); ?></td>
                                <td class="text-end">₹<?php echo number_format($item['unit_price'], 2); ?></td>
                                <td class="text-end">₹<?php echo number_format($item['taxable_value'], 2); ?></td>
                                <td class="text-end"><?php echo $item['tax_rate']; ?>%</td>
                                <td class="text-end fw-bold text-light">₹<?php echo number_format($item['total_amount'], 2); ?></td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>

            <!-- Financial Totals Calculation Box -->
            <div class="row justify-content-end">
                <div class="col-md-6">
                    <div class="p-3 rounded-3 bg-dark border border-secondary border-opacity-25">
                        <div class="d-flex justify-content-between py-1 small">
                            <span class="text-secondary">Subtotal Taxable Amount:</span>
                            <span class="text-light">₹<?php echo number_format($invoice['subtotal_amount'], 2); ?></span>
                        </div>
                        <?php if ($invoice['cgst_amount'] > 0): ?>
                            <div class="d-flex justify-content-between py-1 small">
                                <span class="text-secondary">Central GST (CGST):</span>
                                <span class="text-light">₹<?php echo number_format($invoice['cgst_amount'], 2); ?></span>
                            </div>
                            <div class="d-flex justify-content-between py-1 small">
                                <span class="text-secondary">State GST (SGST):</span>
                                <span class="text-light">₹<?php echo number_format($invoice['sgst_amount'], 2); ?></span>
                            </div>
                        <?php endif; ?>
                        <?php if ($invoice['igst_amount'] > 0): ?>
                            <div class="d-flex justify-content-between py-1 small">
                                <span class="text-warning">Integrated GST (IGST):</span>
                                <span class="text-warning fw-semibold">₹<?php echo number_format($invoice['igst_amount'], 2); ?></span>
                            </div>
                        <?php endif; ?>
                        <div class="d-flex justify-content-between py-1 small border-top border-secondary border-opacity-25">
                            <span class="text-secondary">Total GST Tax:</span>
                            <span class="text-light fw-semibold">₹<?php echo number_format($invoice['total_tax_amount'], 2); ?></span>
                        </div>
                        <?php if ($invoice['discount_amount'] > 0): ?>
                            <div class="d-flex justify-content-between py-1 small text-success">
                                <span>Discount Applied:</span>
                                <span>-₹<?php echo number_format($invoice['discount_amount'], 2); ?></span>
                            </div>
                        <?php endif; ?>
                        <?php if ($invoice['shipping_amount'] > 0): ?>
                            <div class="d-flex justify-content-between py-1 small">
                                <span class="text-secondary">Shipping / Freight:</span>
                                <span class="text-light">₹<?php echo number_format($invoice['shipping_amount'], 2); ?></span>
                            </div>
                        <?php endif; ?>
                        <div class="d-flex justify-content-between py-2 border-top border-secondary border-opacity-50 mt-2">
                            <strong class="text-light fs-5">Grand Total:</strong>
                            <strong class="text-success fs-5">₹<?php echo number_format($invoice['grand_total'], 2); ?></strong>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Sidebar: Bank Details & Metadata -->
    <div class="col-lg-4">
        <!-- Bank Details Card -->
        <div class="glass-card mb-4">
            <h6 class="fw-bold text-light mb-3"><i class="bi bi-bank me-2 text-warning"></i> Bank & Payment Instructions</h6>
            <div class="small">
                <div class="mb-2">
                    <span class="text-secondary d-block">Bank Name:</span>
                    <strong class="text-light"><?php echo htmlspecialchars($invoice['bank_name'] ?: 'Not specified'); ?></strong>
                </div>
                <div class="mb-2">
                    <span class="text-secondary d-block">Account Number:</span>
                    <strong class="text-light font-mono"><?php echo htmlspecialchars($invoice['account_number'] ?: 'Not specified'); ?></strong>
                </div>
                <div class="mb-2">
                    <span class="text-secondary d-block">IFSC Code:</span>
                    <strong class="text-light font-mono"><?php echo htmlspecialchars($invoice['ifsc_code'] ?: 'Not specified'); ?></strong>
                </div>
                <?php if ($invoice['payment_terms']): ?>
                    <div class="mt-3 p-2 rounded bg-dark border border-secondary border-opacity-25">
                        <span class="text-secondary d-block mb-1">Terms:</span>
                        <span class="text-light"><?php echo htmlspecialchars($invoice['payment_terms']); ?></span>
                    </div>
                <?php endif; ?>
            </div>
        </div>

        <!-- Document Audit Card -->
        <div class="glass-card">
            <h6 class="fw-bold text-light mb-3"><i class="bi bi-shield-check me-2 text-info"></i> Extraction Provenance</h6>
            <div class="small">
                <div class="mb-2">
                    <span class="text-secondary d-block">Source Document ID:</span>
                    <code class="text-info"><?php echo htmlspecialchars($invoice['document_id']); ?></code>
                </div>
                <div class="mb-2">
                    <span class="text-secondary d-block">Calibrated Confidence Score:</span>
                    <div class="d-flex align-items-center gap-2 mt-1">
                        <div class="progress flex-grow-1" style="height: 6px;">
                            <div class="progress-bar bg-success" style="width: <?php echo round($invoice['confidence_score'] * 100); ?>%"></div>
                        </div>
                        <span class="badge bg-success"><?php echo round($invoice['confidence_score'] * 100, 1); ?>%</span>
                    </div>
                </div>
                <div class="mb-2">
                    <span class="text-secondary d-block">Verification Mode:</span>
                    <strong class="text-light"><?php echo htmlspecialchars($invoice['verification_type']); ?></strong>
                </div>
                <div>
                    <span class="text-secondary d-block">Committed to MySQL At:</span>
                    <span class="text-light"><?php echo date('M d, Y H:i:s', strtotime($invoice['invoice_date'])); ?></span>
                </div>
            </div>
        </div>
    </div>
</div>
