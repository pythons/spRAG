import logging
from dsrag.config.profiles import PROFILE_PRESETS, DEFAULT_PROFILE
from dsrag.diagnostics import run_diagnostics

# Configure the root dsrag logger with a NullHandler to prevent "No handler found" warnings
# This follows Python best practices for library logging
# Users will need to configure their own handlers if they want to see dsrag logs
logger = logging.getLogger("dsrag")
logger.addHandler(logging.NullHandler())

__all__ = ["PROFILE_PRESETS", "DEFAULT_PROFILE", "run_diagnostics"]
