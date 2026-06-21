"""
RetailOps exception classes.

All custom exceptions used throughout the RetailOps CLI Suite
are defined here for consistent error handling.
"""


class RetailOpsError(Exception):
    """Base exception for all RetailOps errors."""

    def __init__(self, message: str = "An unspecified RetailOps error occurred."):
        self.message = message
        super().__init__(self.message)


class DataValidationError(RetailOpsError):
    """Raised when data fails validation checks."""

    def __init__(self, message: str = "Data validation failed."):
        self.message = message
        super().__init__(self.message)


class FileLoadError(RetailOpsError):
    """Raised when a required file cannot be loaded."""

    def __init__(self, message: str = "Failed to load file."):
        self.message = message
        super().__init__(self.message)


class ReportBuildError(RetailOpsError):
    """Raised when building a report fails."""

    def __init__(self, message: str = "Failed to build report."):
        self.message = message
        super().__init__(self.message)