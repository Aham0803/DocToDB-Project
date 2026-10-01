<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo isset($page_title) ? htmlspecialchars($page_title) : 'DocToDB GST Intelligent Pipeline'; ?> | DocToDB</title>
    
    <!-- Modern Typography: Outfit & Inter -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    
    <!-- Bootstrap 5.3 & Icons -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    
    <!-- Custom Glassmorphic Stylesheet -->
    <link rel="stylesheet" href="<?php echo base_url('public/css/style.css'); ?>">
</head>
<body>
    <!-- Top Navigation Bar -->
    <nav class="navbar navbar-expand-lg sticky-top custom-navbar">
        <div class="container-fluid px-4">
            <a class="navbar-brand d-flex align-items-center gap-2" href="<?php echo base_url(); ?>">
                <div class="brand-icon">
                    <i class="bi bi-file-earmark-diff-fill"></i>
                </div>
                <div class="brand-text">
                    <span class="brand-title">DocTo<span class="gradient-text">DB</span></span>
                    <span class="brand-badge">GST AI</span>
                </div>
            </a>

            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navContent">
                <span class="navbar-toggler-icon"></span>
            </button>

            <div class="collapse navbar-collapse" id="navContent">
                <ul class="navbar-nav me-auto mb-2 mb-lg-0 ms-lg-4 gap-1">
                    <li class="nav-item">
                        <a class="nav-link <?php echo (isset($active_page) && $active_page == 'dashboard') ? 'active' : ''; ?>" href="<?php echo base_url(); ?>">
                            <i class="bi bi-grid-1x2 me-1"></i> Dashboard
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link <?php echo (isset($active_page) && $active_page == 'upload') ? 'active' : ''; ?>" href="<?php echo base_url('upload'); ?>">
                            <i class="bi bi-cloud-arrow-up me-1"></i> Upload Invoices
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link <?php echo (isset($active_page) && $active_page == 'review') ? 'active' : ''; ?>" href="<?php echo base_url('queue'); ?>">
                            <i class="bi bi-shield-exclamation me-1"></i> HITL Review Queue
                            <span class="badge bg-warning text-dark ms-1 pulse-badge">Action Required</span>
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link <?php echo (isset($active_page) && $active_page == 'invoices') ? 'active' : ''; ?>" href="<?php echo base_url('invoices'); ?>">
                            <i class="bi bi-table me-1"></i> Verified Invoices
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link <?php echo (isset($active_page) && $active_page == 'chat') ? 'active' : ''; ?>" href="<?php echo base_url('chat'); ?>">
                            <i class="bi bi-chat-quote-fill me-1 text-primary"></i> RAG AI Assistant
                        </a>
                    </li>
                </ul>

                <div class="d-flex align-items-center gap-3">
                    <div class="status-indicator">
                        <span class="status-dot"></span>
                        <span class="status-label">LangGraph Agent: <strong class="text-success">Active</strong></span>
                    </div>
                    <div class="gst-badge">
                        <i class="bi bi-patch-check-fill text-info"></i>
                        <span>MOD-36 GST Engine</span>
                    </div>
                </div>
            </div>
        </div>
    </nav>

    <!-- Main Container Content -->
    <main class="main-content py-4">
        <div class="container-fluid px-4">
