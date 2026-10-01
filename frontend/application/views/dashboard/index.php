<div class="row g-4 mb-4">
    <!-- Stat 1: Total Documents Ingested -->
    <div class="col-xl-3 col-sm-6">
        <div class="glass-card metric-card">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <span class="text-secondary small text-uppercase fw-semibold">Ingested Documents</span>
                    <div class="metric-value mt-1"><?php echo number_format($stats['total_documents']); ?></div>
                    <span class="text-muted small mt-1 d-block"><i class="bi bi-cpu me-1 text-primary"></i> LangGraph Orchestrated</span>
                </div>
                <div class="metric-icon bg-primary bg-opacity-10 text-primary">
                    <i class="bi bi-file-earmark-text"></i>
                </div>
            </div>
        </div>
    </div>

    <!-- Stat 2: Auto-Approval Precision & Rate -->
    <div class="col-xl-3 col-sm-6">
        <div class="glass-card metric-card success">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <span class="text-secondary small text-uppercase fw-semibold">Auto-Approved Rate</span>
                    <div class="metric-value mt-1"><?php echo $stats['auto_approved_percent']; ?>%</div>
                    <span class="text-success small mt-1 d-block"><i class="bi bi-shield-check me-1"></i> Threshold $\tau = 0.88$ Passed</span>
                </div>
                <div class="metric-icon bg-success bg-opacity-10 text-success">
                    <i class="bi bi-check-all"></i>
                </div>
            </div>
        </div>
    </div>

    <!-- Stat 3: Pending HITL Review Queue -->
    <div class="col-xl-3 col-sm-6">
        <div class="glass-card metric-card warning">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <span class="text-secondary small text-uppercase fw-semibold">Human Review Queue</span>
                    <div class="metric-value mt-1"><?php echo number_format($stats['pending_review_count']); ?></div>
                    <span class="text-warning small mt-1 d-block"><i class="bi bi-exclamation-triangle me-1"></i> Low Confidence / Errors</span>
                </div>
                <div class="metric-icon bg-warning bg-opacity-10 text-warning">
                    <i class="bi bi-person-check"></i>
                </div>
            </div>
        </div>
    </div>

    <!-- Stat 4: Total Verified Spend in MySQL -->
    <div class="col-xl-3 col-sm-6">
        <div class="glass-card metric-card info">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <span class="text-secondary small text-uppercase fw-semibold">Total Verified Spend</span>
                    <div class="metric-value mt-1">₹<?php echo number_format($stats['total_grand_amount'], 2); ?></div>
                    <span class="text-info small mt-1 d-block"><i class="bi bi-receipt me-1"></i> GST: ₹<?php echo number_format($stats['total_tax_amount'], 2); ?></span>
                </div>
                <div class="metric-icon bg-info bg-opacity-10 text-info">
                    <i class="bi bi-currency-rupee"></i>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Middle Section: Quick Ingestion Dropzone & Pipeline Overview -->
<div class="row g-4 mb-4">
    <div class="col-lg-6">
        <div class="glass-card h-100">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="mb-0 fw-bold"><i class="bi bi-cloud-arrow-up-fill me-2 text-primary"></i> Fast Invoice Ingestion</h5>
                <span class="badge bg-secondary">PDF / JPEG / PNG</span>
            </div>
            <p class="text-muted small">Upload an Indian GST invoice or bill. The LangGraph agent extracts structured items, verifies MOD-36 checksum and Place of Supply (POS) rules, and persists clean data into MySQL.</p>
            
            <div class="dropzone-container" id="invoiceDropzone">
                <input type="file" id="invoiceFileInput" class="d-none" accept=".pdf,.png,.jpg,.jpeg,.webp">
                <i class="bi bi-file-earmark-arrow-up-fill dropzone-icon"></i>
                <h6 class="fw-bold mb-1">Drag & Drop Invoice File here, or <span class="text-primary text-decoration-underline">Browse</span></h6>
                <p class="text-muted small mb-0">Max size 15MB &bull; Automatic Multimodal Parsing</p>
            </div>

            <!-- Upload Progress Visualizer -->
            <div id="uploadProgress" class="mt-3 d-none">
                <div class="progress" style="height: 8px;">
                    <div id="progressBar" class="progress-bar progress-bar-striped progress-bar-animated bg-primary" role="progressbar" style="width: 0%"></div>
                </div>
                <small id="uploadStatusText" class="d-block mt-2 text-muted"></small>
            </div>
        </div>
    </div>

    <div class="col-lg-6">
        <div class="glass-card h-100">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="mb-0 fw-bold"><i class="bi bi-diagram-3-fill me-2 text-info"></i> Pipeline Architecture State</h5>
                <span class="badge bg-primary-subtle text-primary border border-primary-subtle">LangGraph Active</span>
            </div>
            
            <div class="d-flex flex-column gap-3">
                <div class="p-3 rounded-3 bg-dark bg-opacity-50 border border-secondary border-opacity-25 d-flex align-items-center gap-3">
                    <div class="rounded-circle p-2 bg-primary bg-opacity-25 text-primary"><i class="bi bi-1-circle-fill fs-5"></i></div>
                    <div>
                        <strong class="d-block text-light">1. Multimodal Vision Extraction</strong>
                        <small class="text-muted">Google Gemini / OpenAI processes PDF and images directly.</small>
                    </div>
                </div>

                <div class="p-3 rounded-3 bg-dark bg-opacity-50 border border-secondary border-opacity-25 d-flex align-items-center gap-3">
                    <div class="rounded-circle p-2 bg-warning bg-opacity-25 text-warning"><i class="bi bi-2-circle-fill fs-5"></i></div>
                    <div>
                        <strong class="d-block text-light">2. GST Domain Rules & Self-Correction Retry</strong>
                        <small class="text-muted">MOD-36 checksum, POS tax splitting (CGST+SGST vs IGST), and 1-pass retry loop.</small>
                    </div>
                </div>

                <div class="p-3 rounded-3 bg-dark bg-opacity-50 border border-secondary border-opacity-25 d-flex align-items-center gap-3">
                    <div class="rounded-circle p-2 bg-success bg-opacity-25 text-success"><i class="bi bi-3-circle-fill fs-5"></i></div>
                    <div>
                        <strong class="d-block text-light">3. Calibrated Confidence & Dual Routing</strong>
                        <small class="text-muted">Score $\ge 0.88 \rightarrow$ Auto-Insert to MySQL + ChromaDB; Else $\rightarrow$ HITL Review Queue.</small>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Bottom Section: HITL Queue & Recent Invoices -->
<div class="row g-4">
    <!-- Queue Card -->
    <div class="col-lg-6">
        <div class="glass-card">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="mb-0 fw-bold"><i class="bi bi-shield-exclamation me-2 text-warning"></i> Documents Pending Human Review</h5>
                <a href="<?php echo base_url('queue'); ?>" class="btn btn-sm btn-outline-warning">View All Queue</a>
            </div>

            <?php if (empty($pending_queue)): ?>
                <div class="text-center py-4 text-muted">
                    <i class="bi bi-check-circle fs-2 text-success d-block mb-2"></i>
                    No documents currently pending review. Pipeline is healthy!
                </div>
            <?php else: ?>
                <div class="table-responsive">
                    <table class="table table-custom table-hover">
                        <thead>
                            <tr>
                                <th>Filename</th>
                                <th>Confidence</th>
                                <th>Reasons / Issues</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($pending_queue as $item): ?>
                                <tr>
                                    <td>
                                        <div class="fw-semibold text-light"><?php echo htmlspecialchars($item['original_filename']); ?></div>
                                        <small class="text-muted"><?php echo htmlspecialchars($item['file_type']); ?></small>
                                    </td>
                                    <td>
                                        <span class="badge bg-warning-subtle text-warning border border-warning-subtle">
                                            <?php echo round($item['composite_confidence'] * 100, 1); ?>%
                                        </span>
                                    </td>
                                    <td>
                                        <?php if (!empty($item['flagged_reasons'])): ?>
                                            <small class="text-danger-emphasis d-block text-truncate" style="max-width: 220px;" title="<?php echo htmlspecialchars(implode(', ', $item['flagged_reasons'])); ?>">
                                                <?php echo htmlspecialchars($item['flagged_reasons'][0]); ?>
                                            </small>
                                        <?php else: ?>
                                            <small class="text-muted">Awaiting human signoff</small>
                                        <?php endif; ?>
                                    </td>
                                    <td>
                                        <a href="<?php echo base_url('review/verify/' . $item['id']); ?>" class="btn btn-sm btn-primary">
                                            <i class="bi bi-pencil-square me-1"></i> Verify
                                        </a>
                                    </td>
                                </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
            <?php endif; ?>
        </div>
    </div>

    <!-- Recent Invoices Card -->
    <div class="col-lg-6">
        <div class="glass-card">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="mb-0 fw-bold"><i class="bi bi-table me-2 text-success"></i> Recently Verified MySQL Invoices</h5>
                <a href="<?php echo base_url('invoices'); ?>" class="btn btn-sm btn-outline-success">View All Invoices</a>
            </div>

            <?php if (empty($recent_invoices)): ?>
                <div class="text-center py-4 text-muted">
                    <i class="bi bi-inbox fs-2 d-block mb-2"></i>
                    No verified invoices in database yet. Ingest an invoice above to begin!
                </div>
            <?php else: ?>
                <div class="table-responsive">
                    <table class="table table-custom table-hover">
                        <thead>
                            <tr>
                                <th>Invoice #</th>
                                <th>Vendor</th>
                                <th>Date</th>
                                <th>Grand Total</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($recent_invoices as $inv): ?>
                                <tr>
                                    <td>
                                        <a href="<?php echo base_url('invoices/view/' . $inv['id']); ?>" class="fw-semibold text-info text-decoration-none">
                                            <?php echo htmlspecialchars($inv['invoice_number']); ?>
                                        </a>
                                    </td>
                                    <td>
                                        <div class="text-light"><?php echo htmlspecialchars($inv['vendor_name']); ?></div>
                                        <small class="text-muted font-mono"><?php echo htmlspecialchars($inv['vendor_gstin']); ?></small>
                                    </td>
                                    <td><?php echo htmlspecialchars($inv['invoice_date']); ?></td>
                                    <td class="fw-bold text-light">₹<?php echo number_format($inv['grand_total'], 2); ?></td>
                                    <td>
                                        <span class="badge bg-success-subtle text-success border border-success-subtle">
                                            <?php echo htmlspecialchars($inv['verification_type']); ?>
                                        </span>
                                    </td>
                                </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
            <?php endif; ?>
        </div>
    </div>
</div>

<script>
    window.UPLOAD_AJAX_URL = "<?php echo base_url('upload/ajax'); ?>";
</script>
