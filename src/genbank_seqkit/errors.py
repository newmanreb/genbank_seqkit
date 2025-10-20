"""
Custom exception classes for the Genbank Seqkit project.

These exceptions help make error handling more readable, consistent,
and testable across the project.
"""

class GenbankError(Exception):
    """Base class for all Genbank Seqkit errors."""
    pass


class GenbankFetchError(GenbankError):
    """Raised when a network request to Entrez fails (e.g. 404, timeout)."""
    def __init__(self, transcript_id: str, message: str = "Failed to fetch record."):
        self.transcript_id = transcript_id
        self.message = f"{message} Transcript ID: {transcript_id}"
        super().__init__(self.message)


class GenbankParseError(GenbankError):
    """Raised when the XML data cannot be parsed correctly."""
    def __init__(self, transcript_id: str, message: str = "Failed to parse XML data."):
        self.transcript_id = transcript_id
        self.message = f"{message} Transcript ID: {transcript_id}"
        super().__init__(self.message)


class GenbankValidationError(GenbankError):
    """Raised when a user provides invalid input (e.g., malformed transcript ID)."""
    def __init__(self, value: str, message: str = "Invalid input."):
        self.value = value
        self.message = f"{message} Value: {value}"
        super().__init__(self.message)


class TranscriptIdError(Exception):
    """
    Custom exception raised when a transcript identifier does not meet the
    expected NCBI format requirements.
    """
    pass

