-- =======================================================
-- Document to Database (DocToDB) - GST Invoicing Schema
-- =======================================================

CREATE DATABASE IF NOT EXISTS `doc_to_db` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE `doc_to_db`;

-- 1. Document Ingestion Queue & Extraction Audit
CREATE TABLE IF NOT EXISTS `documents` (
    `id` VARCHAR(36) PRIMARY KEY,
    `original_filename` VARCHAR(255) NOT NULL,
    `stored_filepath` VARCHAR(500) NOT NULL,
    `file_hash` VARCHAR(64) NOT NULL,
    `file_type` VARCHAR(50) NOT NULL,
    `file_size_bytes` BIGINT NOT NULL,
    `document_type` VARCHAR(50) NOT NULL DEFAULT 'GENERAL_DOCUMENT',
    `document_title` VARCHAR(255) NULL,
    `primary_entity` VARCHAR(255) NULL,
    `summary` TEXT NULL,
    `status` ENUM('QUEUED', 'PROCESSING', 'AUTO_APPROVED', 'PENDING_REVIEW', 'MANUALLY_APPROVED', 'REJECTED', 'DUPLICATE') NOT NULL DEFAULT 'QUEUED',
    `composite_confidence` DECIMAL(5, 4) DEFAULT 0.0000,
    `llm_provider` VARCHAR(50) NOT NULL DEFAULT 'gemini',
    `retry_count` INT NOT NULL DEFAULT 0,
    `flagged_reasons` JSON NULL,
    `extracted_json` LONGTEXT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_doc_status` (`status`),
    INDEX `idx_doc_type` (`document_type`),
    INDEX `idx_doc_hash` (`file_hash`),
    INDEX `idx_doc_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 1b. Universal Document Dynamic Attributes
CREATE TABLE IF NOT EXISTS `universal_records` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `document_id` VARCHAR(36) NOT NULL,
    `document_type` VARCHAR(50) NOT NULL,
    `field_category` VARCHAR(50) NULL,
    `field_key` VARCHAR(100) NOT NULL,
    `field_value` LONGTEXT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_univ_doc` (`document_id`),
    INDEX `idx_univ_type` (`document_type`),
    INDEX `idx_univ_key` (`field_key`),
    CONSTRAINT `fk_univ_doc` FOREIGN KEY (`document_id`) REFERENCES `documents` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- 2. Clean, Structured Financial Invoices
CREATE TABLE IF NOT EXISTS `invoices` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `document_id` VARCHAR(36) NOT NULL,
    `invoice_number` VARCHAR(100) NOT NULL,
    `invoice_date` DATE NOT NULL,
    `due_date` DATE NULL,
    `currency` VARCHAR(10) NOT NULL DEFAULT 'INR',
    `purchase_order_number` VARCHAR(100) NULL,
    `payment_status` ENUM('PENDING', 'PAID', 'OVERDUE', 'PARTIALLY_PAID') NOT NULL DEFAULT 'PENDING',
    
    -- Vendor / Supplier
    `vendor_name` VARCHAR(255) NOT NULL,
    `vendor_gstin` VARCHAR(15) NOT NULL,
    `vendor_state_code` VARCHAR(2) NOT NULL,
    `vendor_address` TEXT NULL,
    `vendor_phone` VARCHAR(50) NULL,
    `vendor_email` VARCHAR(100) NULL,
    `vendor_pan` VARCHAR(10) NULL,
    
    -- Customer / Buyer
    `customer_name` VARCHAR(255) NOT NULL,
    `customer_gstin` VARCHAR(15) NULL,
    `customer_state_code` VARCHAR(2) NULL,
    `place_of_supply` VARCHAR(100) NULL,
    `customer_address` TEXT NULL,
    
    -- Financial Totals
    `subtotal_amount` DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    `cgst_amount` DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    `sgst_amount` DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    `igst_amount` DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    `total_tax_amount` DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    `discount_amount` DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    `shipping_amount` DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    `round_off_amount` DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    `grand_total` DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    
    -- GST Logic Flags
    `is_interstate` BOOLEAN NOT NULL DEFAULT FALSE,
    `reverse_charge` BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Bank / Payment Terms
    `bank_name` VARCHAR(150) NULL,
    `account_number` VARCHAR(60) NULL,
    `ifsc_code` VARCHAR(25) NULL,
    `payment_terms` TEXT NULL,
    
    -- Audit & Confidence
    `verification_type` ENUM('AUTO', 'MANUAL') NOT NULL DEFAULT 'AUTO',
    `confidence_score` DECIMAL(5, 4) NOT NULL DEFAULT 0.0000,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Constraints & Indexes
    CONSTRAINT `fk_invoices_doc` FOREIGN KEY (`document_id`) REFERENCES `documents` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `uq_vendor_invoice` (`vendor_gstin`, `invoice_number`, `invoice_date`),
    INDEX `idx_vendor_gstin` (`vendor_gstin`),
    INDEX `idx_vendor_name` (`vendor_name`),
    INDEX `idx_customer_name` (`customer_name`),
    INDEX `idx_inv_date` (`invoice_date`),
    INDEX `idx_payment_status` (`payment_status`),
    INDEX `idx_grand_total` (`grand_total`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Invoice Line Items
CREATE TABLE IF NOT EXISTS `invoice_items` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `invoice_id` INT NOT NULL,
    `item_index` INT NOT NULL DEFAULT 1,
    `description` TEXT NOT NULL,
    `hsn_sac_code` VARCHAR(15) NULL,
    `quantity` DECIMAL(12, 3) NOT NULL DEFAULT 1.000,
    `unit_of_measure` VARCHAR(30) NULL DEFAULT 'NOS',
    `unit_price` DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    `taxable_value` DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    `tax_rate` DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
    `cgst_rate` DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
    `cgst_amount` DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    `sgst_rate` DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
    `sgst_amount` DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    `igst_rate` DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
    `igst_amount` DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    `total_amount` DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    CONSTRAINT `fk_items_invoice` FOREIGN KEY (`invoice_id`) REFERENCES `invoices` (`id`) ON DELETE CASCADE,
    INDEX `idx_item_hsn` (`hsn_sac_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Human-in-the-Loop Ground Truth Feedback Store
CREATE TABLE IF NOT EXISTS `human_corrections` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `document_id` VARCHAR(36) NOT NULL,
    `reviewer_name` VARCHAR(100) NOT NULL DEFAULT 'system_reviewer',
    `original_extracted_json` LONGTEXT NOT NULL,
    `human_corrected_json` LONGTEXT NOT NULL,
    `field_diffs` JSON NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_corrections_doc` FOREIGN KEY (`document_id`) REFERENCES `documents` (`id`) ON DELETE CASCADE,
    INDEX `idx_corr_doc` (`document_id`),
    INDEX `idx_corr_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Chat History & Routing Audit Trail
CREATE TABLE IF NOT EXISTS `chat_history` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `session_id` VARCHAR(100) NOT NULL,
    `user_query` TEXT NOT NULL,
    `query_type` ENUM('STRUCTURED_SQL_TOOL', 'VECTOR_RAG', 'HYBRID') NOT NULL,
    `tool_called` VARCHAR(100) NULL,
    `retrieved_sources` JSON NULL,
    `assistant_response` TEXT NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_chat_session` (`session_id`),
    INDEX `idx_chat_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
