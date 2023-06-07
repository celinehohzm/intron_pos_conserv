#!/bin/bash
set -x
if [ $# -ne 1 ]; then
    echo "Usage: $0 <protein_id_list.txt>"
    exit 1
fi

orthologs_protein_id_list=$1

# Read the first protein ID and store it in a variable
first_protein_id=$(head -n 1 "$orthologs_protein_id_list")
echo "First protein ID: $first_protein_id"

# Clear the output file
echo "" > sequence_w_introns.fa


# Loop through each protein ID in the list
for protein_id in $(cat "$orthologs_protein_id_list"); do

    echo "Processing ortholog protein ${protein_id}"

    # Fetch the amino_acid_fasta.txt
    efetch -db protein -id "${protein_id}" -format fasta > amino_acid.fa

    # Fetch the whole_table.txt
    esearch -db protein -query "${protein_id}" | elink -target gene | efetch -format gene_table > whole_table.txt

    # Get the target_aa_length
    # target_aa_length=$(grep -v '^>' amino_acid_fasta.txt | tr -d '\n' | wc -m)
    # echo "target_aa_length ${target_aa_length}"

    # Extract the table from whole_table.txt
    python3 1_extract_table.py whole_table.txt ${protein_id} > ${protein_id}_extracted_table.txt

    # Process multi-line fasta files, outputs org_aa_sequence.fasta
    python3 1.5_extract_seq_from_fasta.py amino_acid.fa > ${protein_id}_org_aa_sequence.fa

    # Outputs sequence_w_introns.fasta
    python3 2_extract_n_insert_introns.py ${protein_id}_extracted_table.txt ${protein_id}_org_aa_sequence.fa 

    echo "Completed processing ${protein_id}"

done
