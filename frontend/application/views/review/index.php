<div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3 mb-4">
    <div>
        <h4 class="fw-bold mb-1">
            <i class="bi bi-shield-exclamation text-warning me-2"></i> Human-in-the-Loop Review Queue
        </h4>
        <p class="text-secondary small mb-0">
            Documents flagged by the LangGraph validation engine due to low composite confidence score, GST rule mismatch, or duplicate detection.
        </p>
    </div>
    
    <div class="d-flex gap-2">
        <a href="<?php echo base_url('queue'); ?>" class="btn btn-sm <?php echo empty($status_filter) ? 'btn-primary' : 'btn-outline-secondary'; ?>">
            Pending Review
        </a>
        <a href="<?php echo base_url('queue?status=DUPLICATE'); ?>" class="btn btn-sm <?php echo ($status_filter == 'DUPLICATE') ? 'btn-danger' : 'btn-outline-secondary'; ?>">
            Duplicates
        </a>
        <a href="<?php echo base_url('queue?status=REJECTED'); ?>" class="btn btn-sm <?php echo ($status_filter == 'REJECTED') ? 'btn-secondary' : 'btn-outline-secondary'; ?>">
            Rejected
        </a>
    </div>
</div>

<div class="glass-card">
    <?php if (empty($queue_items)): ?>
        <div class="text-center py-5">
            <i class="bi bi-patch-check-fill text-success" style="font-size: 3rem;"></i>
            <h5 class="fw-bold mt-3 mb-1">All Clear! No Pending Reviews</h5>
            <p class="text-muted small">Every ingested invoice was either automatically approved or verified by an officer.</p>
            <a href="<?php echo base_url('upload'); ?>" class="btn btn-primary btn-sm mt-2">
                <i class="bi bi-cloud-arrow-up me-1"></i> Upload New Invoice
            </a>
        </div>
    <?php else: ?>
        <div class="table-responsive">
            <table class="table table-custom table-hover">
                <thead>
                    <tr>
                        <th>Document</th>
                        <th>Created At</th>
                        <th>Confidence Score</th>
                        <th>Retries</th>
                        <th>Flagged Issues & Violations</th>
                        <th>Status</th>
                        <th class="text-end">Action</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($queue_items as $doc): ?>
                        <tr>
                            <td>
                                <div class="d-flex align-items-center gap-2">
                                    <i class="bi bi-file-earmark-pdf-fill text-danger fs-4"></i>
                                    <div>
                                        <span class="fw-semibold text-light"><?php echo htmlspecialchars($doc['original_filename']); ?></span>
                                        <small class="text-muted d-block font-mono"><?php echo htmlspecialchars($doc['id']); ?></small>
                                    </div>
                                </div>
                            </td>
                            <td>
                                <small class="text-light"><?php echo date('M d, Y H:i', strtotime($doc['created_at'])); ?></small>
                            </td>
                            <td style="min-width: 140px;">
                                <?php 
                                    $score = round($doc['composite_confidence'] * 100, 1); 
                                    $badge_class = ($score >= 88) ? 'bg-success' : (($score >= 70) ? 'bg-warning text-dark' : 'bg-danger');
                                ?>
                                <div class="d-flex align-items-center gap-2">
                                    <div class="progress flex-grow-1" style="height: 6px;">
                                        <div class="progress-bar <?php echo $badge_class; ?>" role="progressbar" style="width: <?php echo $score; ?>%"></div>
                                    </div>
                                    <span class="badge <?php echo $badge_class; ?>"><?php echo $score; ?>%</span>
                                </div>
                            </td>
                            <td>
                                <span class="badge bg-dark border border-secondary text-secondary">
                                    <?php echo $doc['retry_count']; ?> Retries
                                </span>
                            </td>
                            <td style="max-width: 320px;">
                                <?php if (!empty($doc['flagged_reasons'])): ?>
                                    <ul class="list-unstyled mb-0 small">
                                        <?php foreach (array_slice($doc['flagged_reasons'], 0, 2) as $reason): ?>
                                            <li class="text-warning-emphasis text-truncate mb-1" title="<?php echo htmlspecialchars($reason); ?>">
                                                <i class="bi bi-exclamation-circle me-1 text-warning"></i><?php echo htmlspecialchars($reason); ?>
                                            </li>
                                        <?php endforeach; ?>
                                        <?php if (count($doc['flagged_reasons']) > 2): ?>
                                            <li class="text-muted fst-italic">+<?php echo count($doc['flagged_reasons']) - 2; ?> more issues...</li>
                                        <?php endif; ?>
                                    </ul>
                                <?php else: ?>
                                    <small class="text-muted">Awaiting human sign-off</small>
                                <?php endif; ?>
                            </td>
                            <td>
                                <span class="badge bg-warning-subtle text-warning border border-warning-subtle">
                                    <?php echo htmlspecialchars($doc['status']); ?>
                                </span>
                            </td>
                            <td class="text-end">
                                <a href="<?php echo base_url('review/verify/' . $doc['id']); ?>" class="btn btn-sm btn-primary">
                                    <i class="bi bi-pencil-square me-1"></i> Verify & Correct
                                </a>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    <?php endif; ?>
</div>
