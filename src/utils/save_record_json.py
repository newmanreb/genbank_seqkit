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

def save_record_json(transcript_id: str, filename: str = None,
                     data_dir: Path = Path(__file__).resolve().parents[2] / "test_data",
                     pretty_print: bool = False) -> Path:
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
    Exception
        If fetching or saving the record fails.
    """

    try:
        # Create a .json file to store the record in test_data
        data_dir.mkdir(parents=True, exist_ok=True)
        if filename is None:
            filename = data_dir / f"{transcript_id}.json"
        else:
            filename = Path(filename)

        # Fetch the record
        logger.debug(f"Fetching transcript record {transcript_id} to {filename}...")
        record = fetch_transcript_record(transcript_id)

        # Pretty-print to console if requested
        if pretty_print:
            pprint(record)

        # Save the record
        with open(filename, "w") as f:
            json.dump(record, f, indent=2)

        # Log success
        logger.debug(f"Record for {transcript_id} saved to {filename}")

        return filename

    except Exception as e:
        logger.error(f"Failed to save record for {transcript_id}: {e}")
        raise

if __name__ == "__main__": # pragma: no cover

    save_record_json(transcript_id="NM_000067.3")