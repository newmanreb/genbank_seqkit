from utils.entrez_efetch import fetch_transcript_record
from genbank_seqkit.logger import logger

class Transcript:
    """
    Represents a GenBank transcript record. Automatically fetches data from NCBI and populates key attributes.
    """
    def __init__(self, transcript_id: str):
        # Core attributes
        self.transcript_id = transcript_id
        self.gene_symbol = None
        self.hgnc_id = None
        self.dna_sequence = None
        self.rna_sequence = None
        self.protein_sequence = None
        self.protein_id = None

        # Fetch and populate attributes automatically
        self._fetch_and_populate()

    def _fetch_and_populate(self):
        """
        Internal method to fetch the GenBank record using entrez_efetch and populate key attributes.
        """
        try:
            record = fetch_transcript_record(self.transcript_id)

            # Top-level fields:
            self.transcript_id = record.get('GBSeq_accession-version', self.transcript_id)
            self.dna_sequence = record['GBSeq_sequence'].upper()
            self.rna_sequence = self.dna_sequence.replace('T', 'U')

            # TODO: Parse features for gene_symbol, hgnc_id, protein_sequence, protein_id
            # for feature in record[...

        except Exception as e:
            logger.error(f"Failed to fetch transcript {self.transcript_id}: {e}")
            raise

    def as_fasta(self, sequence:str) -> str:
        """
        Return FASTA formatted sequence string for the given sequence.
        :param sequence:
        :return:
        """
        # TODO: Implement proper GenBank formatting.
        return

    def __repr__(self):
        return f"<Transcript {self.transcript_id}>"

# Demo
if __name__ == "__main__":
    t = Transcript("NM_000093.5")
    print(t.transcript_id)
    print(t.dna_sequence[:50])  # first 50 bases
    print(t.as_fasta(t.dna_sequence))

