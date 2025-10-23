# save_record_json.py
# Utility to fetch a GenBank transcript record from NCBI and save it as a JSON file for offline inspection, testing,
# or development.

import sys
import json
from pprint import pprint
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))    # Adds utils/ folder to path
from entrez_efetch import fetch_transcript_record
from genbank_seqkit.logger import logger
from genbank_seqkit.errors import (
    GenbankFetchError,
    GenbankParseError,
    TranscriptIdError,
    GenbankError,
)

def save_record_json(transcript_id: str,
                     filename: str = None,
                     data_dir: Path = Path(__file__).resolve().parents[2] / "test_data",
                     pretty_print: bool = False,
                     ) -> Path:
    """
    Fetch a GenBank transcript record and save it as a JSON file.

    Parameters
    ------------
    transcript_id : str
        RefSeq transcript ID (e.g., "NM_000093.5").
    filename : str or Path, optional
        Path to save the JSON file. Defaults to "{transcript_id}.json" in data_dir.
    data_dir : Path, optional
        Directory to save the JSON file. Defaults to top-level test_data folder.
    pretty_print : bool, optional
        If True, pretty-prints the record to console for inspection.

    Returns
    ------------
    Path
        The full path to the saved JSON file.

    Raises
    ------------
    TranscriptIdError
        If the provided transcript ID is invalid.
    GenbankFetchError
        If the record cannot be fetched from Entrez.
    GenbankParseError
        If the XML data cannot be parsed.
    GenbankError
        If saving the record fails for any other reason (e.g. file write issues).
    """

    try:
        data_dir.mkdir(parents=True, exist_ok=True)                 # Create directory if missing
        if filename is None:                                        # Default filename
            filename = data_dir / f"{transcript_id}.json"           # .json file created
        else:
            filename = Path(filename)

        # Fetch the record (may raise TranscriptIdError, GenbankFetchError, or GenbankParseError)
        logger.debug(f"Fetching transcript record {transcript_id} to {filename}...")
        record = fetch_transcript_record(transcript_id)

        if pretty_print:                                            # Pretty-print to console if requested
            pprint(record)

        with open(filename, "w") as f:                              # Save the record
            json.dump(record, f, indent=2)                          # indent=2 provides pretty indentation

        logger.debug(f"Record for {transcript_id} saved to {filename}") # Log success

        return filename

    except (TranscriptIdError, GenbankFetchError, GenbankParseError):
        raise                                                       # Raise these exceptions unchanged

    except Exception as e:                                          # Catch-all exception for unexpected issues
        logger.error(f"Unexpected error saving record for {transcript_id}: {e}")
        raise GenbankError (f"Failed to save record: {e}") from e

if __name__ == "__main__": # pragma: no cover

    save_record_json(transcript_id="NM_000093.5")