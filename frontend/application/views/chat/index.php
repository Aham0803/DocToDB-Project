<div class="row justify-content-center">
    <div class="col-lg-10">
        <!-- Header -->
        <div class="d-flex justify-content-between align-items-center mb-3">
            <div>
                <h4 class="fw-bold mb-1">
                    <i class="bi bi-chat-quote-fill text-primary me-2"></i> AI Financial Document Assistant
                </h4>
                <p class="text-secondary small mb-0">
                    Dual Query Engine: Automatically routes structured aggregations to safe MySQL tools, and document policy/terms queries to ChromaDB Vector RAG.
                </p>
            </div>
            <div>
                <span class="badge bg-primary-subtle text-primary border border-primary-subtle px-3 py-2">
                    <i class="bi bi-cpu-fill me-1"></i> Gemini Flash + ChromaDB RAG
                </span>
            </div>
        </div>

        <!-- Suggestion Chips Bar -->
        <div class="glass-card mb-3 p-3">
            <span class="small text-muted d-block mb-2 fw-semibold">Quick Query Suggestions (Click to Ask):</span>
            <div class="d-flex flex-wrap gap-2">
                <button type="button" class="btn btn-xs btn-outline-info suggestion-chip">
                    "Show all unpaid invoices with pending balance"
                </button>
                <button type="button" class="btn btn-xs btn-outline-info suggestion-chip">
                    "Total spend and GST collected across all vendors"
                </button>
                <button type="button" class="btn btn-xs btn-outline-info suggestion-chip">
                    "Show details for invoice INV-2026-0891"
                </button>
                <button type="button" class="btn btn-xs btn-outline-info suggestion-chip">
                    "What payment terms and bank account are mentioned for Apex Cloud?"
                </button>
            </div>
        </div>

        <!-- Chat Container Box -->
        <div class="glass-card chat-container p-0">
            <!-- Messages Stream Area -->
            <div id="chatMessages" class="chat-messages">
                <!-- Welcome Assistant Message -->
                <div class="chat-bubble assistant">
                    <span class="badge bg-success-subtle text-success border border-success-subtle mb-2">
                        <i class="bi bi-robot me-1"></i> DocToDB Engine Ready
                    </span>
                    <div class="message-content">
                        Namaste! I am your <strong>DocToDB Financial Assistant</strong>. You can ask me questions about your uploaded invoices, taxes, vendors, and payment terms.<br><br>
                        - <strong>Structured Questions:</strong> <em>"Vendor Acme ke pending balance wale saare invoices"</em> (Executed via safe, deterministic MySQL tools).<br>
                        - <strong>Semantic / Text Questions:</strong> <em>"What is the refund policy or IFSC code on invoice 1042?"</em> (Retrieved via ChromaDB vector chunks).
                    </div>
                </div>
            </div>

            <!-- Chat Input Footer -->
            <div class="p-3 bg-dark bg-opacity-75 border-top border-secondary border-opacity-25">
                <form id="chatForm" class="d-flex gap-2">
                    <input type="text" id="chatInput" class="form-control bg-dark text-light border-secondary" 
                        placeholder="Ask anything about invoices, GST calculations, or vendor terms..." autocomplete="off" required>
                    <button type="submit" class="btn btn-primary px-4 d-flex align-items-center gap-2">
                        <span>Send</span>
                        <i class="bi bi-send-fill"></i>
                    </button>
                </form>
            </div>
        </div>
    </div>
</div>

<script>
    window.CHAT_SEND_URL = "<?php echo base_url('chat/send'); ?>";
</script>
