import logging
from dsrag.config.profiles import PROFILE_PRESETS, DEFAULT_PROFILE
from dsrag.diagnostics import run_diagnostics
from dsrag.templates import (
    VERTICAL_TEMPLATES,
    list_vertical_templates,
    get_vertical_template,
    apply_template_to_add_document_kwargs,
    apply_template_to_query_kwargs,
    create_kb_from_template,
    query_with_template,
)

# Configure the root dsrag logger with a NullHandler to prevent "No handler found" warnings
# This follows Python best practices for library logging
# Users will need to configure their own handlers if they want to see dsrag logs
logger = logging.getLogger("dsrag")
logger.addHandler(logging.NullHandler())

__all__ = [
    "PROFILE_PRESETS",
    "DEFAULT_PROFILE",
    "run_diagnostics",
    "VERTICAL_TEMPLATES",
    "list_vertical_templates",
    "get_vertical_template",
    "apply_template_to_add_document_kwargs",
    "apply_template_to_query_kwargs",
    "create_kb_from_template",
    "query_with_template",
]
