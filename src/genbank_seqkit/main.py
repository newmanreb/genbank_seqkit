import sys

from utils.entrez_efetch import fetch_transcript_record
from genbank_seqkit.logger import logger
from utils._force_list import _force_list

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
        self.length = None
        self.mol_type = None
        self.gene_name = None

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
            self.length = record.get("GBSeq_length")
            self.mol_type = record.get("GBSeq_moltype")
            self.gene_name = record.get("GBSeq_definition")

            # Parse feature table
            features = _force_list(record.get("GBSeq_feature-table", {}).get("GBFeature"), verbose=False)
            for feature in features:
                key = feature.get("GBFeature_key")
                quals = _force_list(feature.get("GBFeature_quals", {}).get("GBQualifier"), verbose=False)

                # Gene symbol and HGNC ID
                if key == "gene":
                    for q in quals:
                        if q.get("GBQualifier_name") == "gene":
                            self.gene_symbol = q.get("GBQualifier_value")
                        elif q.get("GBQualifier_name") == "db_xref":
                            if q.get("GBQualifier_value", "").startswith("HGNC:"):
                                self.hgnc_id = q.get("GBQualifier_value").replace("HGNC:", "")

                # CDS and protein info
                elif key == "CDS":
                    for q in quals:
                        if q.get("GBQualifier_name") == "translation":
                            self.protein_sequence = q.get("GBQualifier_value")
                        elif q.get("GBQualifier_name") == "protein_id":
                            self.protein_id = q.get("GBQualifier_value")

        except TranscriptIdError as e:
            logger.error(f"Invalid transcript ID: {self.transcript_id} - {e}")
            raise

        except Exception as e:
            logger.error(f"Failed to fetch transcript {self.transcript_id}: {e}")
            raise

    def as_fasta(self, sequence=None, seq_type="DNA"):
        """
        Return FASTA formatted sequence string for the given sequence.
        Defaults to the DNA transcript sequence if none is provided.
        Logs warnings if the sequence is missing and errors for unknown types.

        Parameters
        ------------
        sequence : str, optional
            The sequence to format. Defaults to self.dna_sequence.
        seq_type: str, optional
            The type of sequence to return, can be "DNA", "RNA" or "protein". Defaults to "DNA".

        Returns
        ------------
        str
            FASTA formatted string.

        Raises
        ------------
        ValueError
            If unknown seq_type is input.

        """
        if sequence is None:
            if seq_type.upper() == "DNA":
                sequence = self.dna_sequence
            elif seq_type.upper() == "RNA":
                sequence = self.rna_sequence
            elif seq_type.upper() == "protein":
                sequence = self.protein_sequence
            else:
                logger.error(f"Unknown sequence type requested: {seq_type}")
                raise ValueError(f"Unknown seq_type: {seq_type}")

        if sequence is None or sequence == "":
            logger.warning(f"{seq_type} sequence not available for {self.transcript_id}")
            sequence = ""

        header = f">{self.transcript_id} | {seq_type}"
        fasta_str = f"{header}\n{sequence}"

        logger.debug(f"Generated FASTA formatted sequence for {self.transcript_id}, seq_type: {seq_type}")
        return fasta_str

    def as_genbank(self, sequence=None, seq_type="DNA"):
        """
        Return a simple GenBank-like formatted string.
        Defaults to the DNA transcript sequence if none is provided.

        Parameters
        ------------
        sequence: str, optional
            The sequence to format. Defaults to self.dna_sequence.
        seq_type: str, optional
            The type of sequence to return. Defaults to "DNA".

        Returns
        ------------
        str
            Simple GenBank-like formatted string.

        Raises
        ------------
        ValueError: If unknown seq_type is input.

        """
        if sequence is None:
            if seq_type.upper() == "DNA":
                sequence = self.dna_sequence
            elif seq_type.upper() == "RNA":
                sequence = self.rna_sequence
            elif seq_type.upper() == "protein":
                sequence = self.protein_sequence
            else:
                raise ValueError(f"Unknown seq_type: {seq_type}")

        if sequence is None or sequence == "":
            logger.warning(f"{seq_type} sequence not available for {self.transcript_id}")
            sequence = ""

        genbank_str = (
            f"LOCUS        {self.transcript_id}\n"
            f"DEFINITION   {seq_type} sequence\n"
            f"ORIGIN\n{sequence}\n//"
        )

        logger.debug(f"Generated GenBank string for {self.transcript_id}, seq_type: {seq_type}")
        return genbank_str

    def __repr__(self):
        return f"<Transcript {self.transcript_id}>"

# Demo
if __name__ == "__main__":

    # import pprint
    # import json
    #
    # record = fetch_transcript_record("NM_000093.5")
    # pprint.pprint(record)
    #
    # with open("record.json", "w") as f:
    #     json.dump(record,f, indent = 2)


    t = Transcript("NM_000093.5")
    print(t.transcript_id)
    print(t.dna_sequence[:50])  # first 50 bases
    print(t.as_fasta(t.dna_sequence))
    print(t.length)
    print(t.mol_type)
    print(t.gene_symbol)
    print(t.protein_sequence)
    print(t.hgnc_id)
    print(t.as_fasta())
    print(t.as_genbank(seq_type="RNA"))

