<div class="row justify-content-center">
    <div class="col-lg-8">
        <div class="glass-card mb-4">
            <div class="d-flex align-items-center justify-content-between mb-3">
                <h4 class="fw-bold mb-0">
                    <i class="bi bi-cloud-arrow-up-fill me-2 text-primary"></i> Upload Financial Invoices & Bills
                </h4>
                <a href="<?php echo base_url('invoices'); ?>" class="btn btn-sm btn-outline-secondary">
                    <i class="bi bi-arrow-left me-1"></i> Back to Invoices
                </a>
            </div>
            <p class="text-secondary">
                Upload Indian GST Tax Invoices in PDF or image format (PNG, JPG, WebP). The self-correcting LangGraph pipeline will parse line items, run MOD-36 checksum checks, and route high-confidence invoices straight into MySQL.
            </p>

            <!-- Extraction Provider Selection -->
            <div class="row g-3 mb-4 p-3 rounded-3 bg-dark bg-opacity-50 border border-secondary border-opacity-25 align-items-center">
                <div class="col-md-5">
                    <label for="providerSelect" class="form-label small fw-semibold text-light mb-1">
                        <i class="bi bi-sliders me-1 text-primary"></i> Extraction LLM Provider:
                    </label>
                    <select id="providerSelect" class="form-select form-select-sm bg-dark text-light border-secondary">
                        <option value="gemini" selected>Google Gemini 2.0 Flash (Multimodal Native - Fast)</option>
                        <option value="openai">OpenAI GPT-4o-mini (Vision API)</option>
                        <option value="ollama">Local Ollama LLaVA (Air-Gapped Private)</option>
                    </select>
                </div>
                <div class="col-md-7">
                    <small class="text-muted d-block">
                        <strong>Calibrated Confidence:</strong> Extracted fields undergo GST state rule validation, MOD-36 check digit, and math reconciliation. Auto-approved only if score $\ge 88\%$.
                    </small>
                </div>
            </div>

            <!-- Upload Dropzone -->
            <div class="dropzone-container" id="invoiceDropzone">
                <input type="file" id="invoiceFileInput" class="d-none" accept=".pdf,.png,.jpg,.jpeg,.webp">
                <i class="bi bi-file-earmark-arrow-up-fill dropzone-icon"></i>
                <h5 class="fw-bold mb-2">Drag & Drop Invoice File here, or <span class="text-primary text-decoration-underline">Choose File</span></h5>
                <p class="text-muted small mb-0">Accepted Formats: PDF, PNG, JPEG, JPG, WebP (Max 15MB)</p>
            </div>

            <!-- Live Status & Progress -->
            <div id="uploadProgress" class="mt-4 d-none">
                <div class="d-flex justify-content-between small text-muted mb-1">
                    <span>LangGraph Workflow In-Flight</span>
                    <span id="progressPercent">Processing...</span>
                </div>
                <div class="progress" style="height: 10px;">
                    <div id="progressBar" class="progress-bar progress-bar-striped progress-bar-animated bg-primary" role="progressbar" style="width: 0%"></div>
                </div>
                <div id="uploadStatusText" class="mt-3 p-3 rounded-3 bg-dark border border-secondary border-opacity-25 small text-light"></div>
            </div>
        </div>

        <!-- Compliance & Pipeline Info Box -->
        <div class="glass-card">
            <h6 class="fw-bold text-light mb-3"><i class="bi bi-info-circle-fill text-info me-2"></i> Indian GST Pipeline Protections</h6>
            <div class="row g-3 small text-muted">
                <div class="col-sm-6">
                    <div class="p-2 rounded bg-dark bg-opacity-25 border border-secondary border-opacity-10">
                        <strong class="text-light d-block mb-1"><i class="bi bi-shield-check text-success me-1"></i> MOD-36 Check Digit Validation</strong>
                        Validates the 15th checksum character of Supplier & Buyer GSTIN against the official GST Council algorithm.
                    </div>
                </div>
                <div class="col-sm-6">
                    <div class="p-2 rounded bg-dark bg-opacity-25 border border-secondary border-opacity-10">
                        <strong class="text-light d-block mb-1"><i class="bi bi-shuffle text-warning me-1"></i> Place of Supply (POS) Logic</strong>
                        Enforces CGST + SGST for Intra-State (State code matching) and IGST for Inter-State transactions.
                    </div>
                </div>
                <div class="col-sm-6">
                    <div class="p-2 rounded bg-dark bg-opacity-25 border border-secondary border-opacity-10">
                        <strong class="text-light d-block mb-1"><i class="bi bi-arrow-repeat text-primary me-1"></i> Self-Correction Retry Loop</strong>
                        If math or GST rules fail, the agent reprompts the LLM with the exact error diagnostic before sending to human review.
                    </div>
                </div>
                <div class="col-sm-6">
                    <div class="p-2 rounded bg-dark bg-opacity-25 border border-secondary border-opacity-10">
                        <strong class="text-light d-block mb-1"><i class="bi bi-files text-danger me-1"></i> Duplicate Protection</strong>
                        Deduplicates files on SHA-256 file hash and compound index on <code>(vendor_gstin, invoice_number, invoice_date)</code>.
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
    window.UPLOAD_AJAX_URL = "<?php echo base_url('upload/ajax'); ?>";
</script>
