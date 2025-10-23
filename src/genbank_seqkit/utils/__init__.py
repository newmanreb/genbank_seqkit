"""
Utility subpackage for Genbank Seqkit.

Contains helper functions for fetching, saving, and normalising data.
"""

from ._force_list import _force_list
from .save_record_json import save_record_json
from .entrez_efetch import fetch_transcript_record

__all__ = ["_force_list", "save_record_json", "fetch_transcript_record"]