import logging
from langgraph.graph import StateGraph, END
from app.agents.state import InvoiceAgentState
from app.agents.nodes import (
    deduplication_node,
    extractor_node,
    validator_node,
    refinement_node,
    storage_node,
)
from app.config import settings

logger = logging.getLogger(__name__)

def route_after_dedup(state: InvoiceAgentState) -> str:
    """Route after deduplication check."""
    if state.get("is_duplicate"):
        return "storage"
    return "extractor"

def route_after_extraction(state: InvoiceAgentState) -> str:
    """Route after initial extraction."""
    if state.get("status") == "FAILED" or not state.get("extracted_data"):
        return "storage"
    return "validator"

def route_after_validation(state: InvoiceAgentState) -> str:
    """
    Core branching logic:
    - Auto-Approve if confidence passes and zero hard errors
    - Refine / Retry if errors found and retry_count < MAX_RETRIES
    - Send to Storage (which queues as PENDING_REVIEW for HITL) if retries exhausted
    """
    if state.get("should_auto_approve"):
        logger.info(f"Invoice passed all GST rules with score {state.get('composite_confidence')}. Routing to AUTO_APPROVE.")
        return "storage"

    retry_count = state.get("retry_count", 0)
    max_retries = settings.MAX_SELF_CORRECTION_RETRIES

    if retry_count < max_retries:
        logger.info(f"Validation failed (retry {retry_count}/{max_retries}). Routing to Refinement Node.")
        return "refinement"

    logger.info("Validation retries exhausted. Routing to Human-in-the-Loop Review Queue.")
    return "storage"


def build_invoice_agent():
    """Compiles the complete LangGraph pipeline."""
    workflow = StateGraph(InvoiceAgentState)

    # Add Nodes
    workflow.add_node("deduplication", deduplication_node)
    workflow.add_node("extractor", extractor_node)
    workflow.add_node("validator", validator_node)
    workflow.add_node("refinement", refinement_node)
    workflow.add_node("storage", storage_node)

    # Set Entry Point
    workflow.set_entry_point("deduplication")

    # Add Conditional Edges
    workflow.add_conditional_edges(
        "deduplication",
        route_after_dedup,
        {
            "extractor": "extractor",
            "storage": "storage"
        }
    )

    workflow.add_conditional_edges(
        "extractor",
        route_after_extraction,
        {
            "validator": "validator",
            "storage": "storage"
        }
    )

    workflow.add_conditional_edges(
        "validator",
        route_after_validation,
        {
            "storage": "storage",
            "refinement": "refinement"
        }
    )

    # Refinement routes back to validator for re-verification!
    workflow.add_edge("refinement", "validator")

    # Storage leads to completion
    workflow.add_edge("storage", END)

    app = workflow.compile()
    return app

# Compiled pipeline instance
invoice_agent_pipeline = build_invoice_agent()
