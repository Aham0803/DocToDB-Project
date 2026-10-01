<div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3 mb-4">
    <div>
        <h4 class="fw-bold mb-1">
            <i class="bi bi-database-check text-success me-2"></i> Verified MySQL Invoices
        </h4>
        <p class="text-secondary small mb-0">
            Clean, validated financial invoices stored in normalized MySQL tables with full GST audit trails.
        </p>
    </div>
    
    <div class="d-flex gap-2">
        <a href="<?php echo base_url('invoices/export'); ?>" class="btn btn-sm btn-outline-info">
            <i class="bi bi-file-earmark-spreadsheet me-1"></i> Export to CSV
        </a>
        <a href="<?php echo base_url('upload'); ?>" class="btn btn-sm btn-primary">
            <i class="bi bi-cloud-arrow-up me-1"></i> Upload New
        </a>
    </div>
</div>

<!-- Search & Filter Bar -->
<div class="glass-card mb-4 p-3">
    <form method="GET" action="<?php echo base_url('invoices'); ?>" class="row g-2 align-items-center">
        <div class="col-md-5">
            <div class="input-group input-group-sm">
                <span class="input-group-text bg-dark text-muted border-secondary"><i class="bi bi-search"></i></span>
                <input type="text" name="search" class="form-control bg-dark text-light border-secondary" 
                    placeholder="Search by Invoice #, Vendor Name, GSTIN..." value="<?php echo htmlspecialchars($search); ?>">
            </div>
        </div>
        <div class="col-md-3">
            <select name="status" class="form-select form-select-sm bg-dark text-light border-secondary">
                <option value="">All Payment Statuses</option>
                <option value="PENDING" <?php echo ($status_filter == 'PENDING') ? 'selected' : ''; ?>>Pending</option>
                <option value="PAID" <?php echo ($status_filter == 'PAID') ? 'selected' : ''; ?>>Paid</option>
                <option value="OVERDUE" <?php echo ($status_filter == 'OVERDUE') ? 'selected' : ''; ?>>Overdue</option>
            </select>
        </div>
        <div class="col-md-2">
            <button type="submit" class="btn btn-sm btn-outline-primary w-100">
                <i class="bi bi-funnel me-1"></i> Filter
            </button>
        </div>
        <?php if (!empty($search) || !empty($status_filter)): ?>
            <div class="col-md-2">
                <a href="<?php echo base_url('invoices'); ?>" class="btn btn-sm btn-outline-secondary w-100">
                    <i class="bi bi-x-circle me-1"></i> Reset
                </a>
            </div>
        <?php endif; ?>
    </form>
</div>

<!-- Invoices Table Card -->
<div class="glass-card">
    <?php if (empty($invoices)): ?>
        <div class="text-center py-5 text-muted">
            <i class="bi bi-inbox fs-1 d-block mb-2"></i>
            <h6 class="fw-bold">No Verified Invoices Found</h6>
            <p class="small">Upload an invoice to have it processed and stored here.</p>
        </div>
    <?php else: ?>
        <div class="table-responsive">
            <table class="table table-custom table-hover">
                <thead>
                    <tr>
                        <th>Invoice #</th>
                        <th>Date</th>
                        <th>Vendor Details</th>
                        <th>Customer</th>
                        <th>Tax Breakdown</th>
                        <th>Grand Total</th>
                        <th>Payment</th>
                        <th>Approval</th>
                        <th class="text-end">Action</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($invoices as $inv): ?>
                        <tr>
                            <td>
                                <a href="<?php echo base_url('invoices/view/' . $inv['id']); ?>" class="fw-bold text-info text-decoration-none">
                                    <?php echo htmlspecialchars($inv['invoice_number']); ?>
                                </a>
                                <small class="text-muted d-block font-mono">ID: #<?php echo $inv['id']; ?></small>
                            </td>
                            <td>
                                <span class="text-light"><?php echo htmlspecialchars($inv['invoice_date']); ?></span>
                                <?php if ($inv['due_date']): ?>
                                    <small class="text-muted d-block">Due: <?php echo htmlspecialchars($inv['due_date']); ?></small>
                                <?php endif; ?>
                            </td>
                            <td>
                                <div class="fw-semibold text-light"><?php echo htmlspecialchars($inv['vendor_name']); ?></div>
                                <span class="badge bg-dark border border-secondary text-info font-mono">
                                    <?php echo htmlspecialchars($inv['vendor_gstin']); ?>
                                </span>
                            </td>
                            <td>
                                <span class="text-light"><?php echo htmlspecialchars($inv['customer_name']); ?></span>
                            </td>
                            <td>
                                <small class="d-block text-secondary">CGST: ₹<?php echo number_format($inv['cgst'], 2); ?></small>
                                <small class="d-block text-secondary">SGST: ₹<?php echo number_format($inv['sgst'], 2); ?></small>
                                <?php if ($inv['igst'] > 0): ?>
                                    <small class="d-block text-warning">IGST: ₹<?php echo number_format($inv['igst'], 2); ?></small>
                                <?php endif; ?>
                            </td>
                            <td>
                                <strong class="text-light fs-6">₹<?php echo number_format($inv['grand_total'], 2); ?></strong>
                            </td>
                            <td>
                                <?php
                                    $p_class = ($inv['payment_status'] == 'PAID') ? 'bg-success' : (($inv['payment_status'] == 'OVERDUE') ? 'bg-danger' : 'bg-warning text-dark');
                                ?>
                                <span class="badge <?php echo $p_class; ?>">
                                    <?php echo htmlspecialchars($inv['payment_status']); ?>
                                </span>
                            </td>
                            <td>
                                <span class="badge <?php echo ($inv['verification_type'] == 'AUTO') ? 'bg-success-subtle text-success border border-success-subtle' : 'bg-info-subtle text-info border border-info-subtle'; ?>">
                                    <?php echo htmlspecialchars($inv['verification_type']); ?>
                                </span>
                            </td>
                            <td class="text-end">
                                <a href="<?php echo base_url('invoices/view/' . $inv['id']); ?>" class="btn btn-xs btn-outline-primary">
                                    <i class="bi bi-eye"></i> Details
                                </a>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    <?php endif; ?>
</div>
