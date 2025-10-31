#!/usr/bin/env python3
"""
Main entry point for the Genbank Seqkit project.

Demonstrates usage of the Transcript class, fetching GenBank records,
and generating FASTA/GenBank-style outputs.
"""

import sys
from genbank_seqkit.logger import logger
from genbank_seqkit.errors import (
    TranscriptIdError,
    GenbankFetchError,
    GenbankParseError,
    GenbankError
)
from genbank_seqkit.transcript import Transcript  # Your Transcript class

def main(transcript_id: str, verbose: bool = False):
    """
    Fetch a transcript from NCBI and print summary, FASTA, and GenBank formats.

    Parameters
    ----------
    transcript_id : str
        RefSeq transcript ID (e.g., "NM_000093.5").
    verbose : bool, optional
        If True, prints debug logging information.
    """
    try:
        # Create Transcript object (fetches and populates automatically)
        transcript = Transcript(transcript_id, verbose=verbose)

        # Print user-friendly summary
        print(transcript)

        # Generate FASTA output
        fasta_str = transcript.as_fasta(seq_type="DNA")
        print("\nFASTA format:\n", fasta_str)

        # Generate simple GenBank output
        genbank_str = transcript.as_genbank(seq_type="DNA")
        print("\nGenBank format:\n", genbank_str)

    except TranscriptIdError as e:
        logger.error(f"Invalid transcript ID: {e}")
        print(f"Error: {e}")

    except (GenbankFetchError, GenbankParseError) as e:
        logger.error(f"Problem retrieving/parsing transcript {transcript_id}: {e}")
        print(f"Error: {e}")

    except GenbankError as e:
        logger.error(f"Unexpected GenBank error for {transcript_id}: {e}")
        print(f"Error: {e}")

    except Exception as e:
        logger.error(f"Unexpected failure for {transcript_id}: {e}")
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <transcript_id>")
        sys.exit(1)

    transcript_id = sys.argv[1]
    main(transcript_id, verbose=True)