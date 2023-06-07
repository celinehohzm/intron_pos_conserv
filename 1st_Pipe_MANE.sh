#!/bin/bash
set -x
if [ $# -ne 1 ]; then
    echo "Usage: $0 <protein_id_list.txt>"
    exit 1
fi

MANE_protein_id_list=$1

# Clear the output file

echo "" > sequence_w_introns.fasta
echo "" >reorder_aln_seq_w_introns.afa

# Loop through each protein ID in the list
for MANE_protein_id in $(cat "$MANE_protein_id_list"); do

    echo "Processing MANE protein ${MANE_protein_id}"

    # Create a directory for the protein_id
    mkdir -p "${MANE_protein_id}"

    # outputs ${MANE_protein_id}.fasta
    python3 1_MANE_pipe_extract_protein_fasta_from_multifasta.py ${MANE_protein_id} MANE.GRCh38.v1.0.refseq_protein.faa

    # outputs blastp orthologs
    /ccb/sw/bin/blastp -query ${MANE_protein_id}.fasta -db refseq_protein -entrez_query "txid7742[ORGN]" -out ${MANE_protein_id}_orthologs.txt -outfmt "6 std staxids scomname ssciname" -remote

    # filter alignment
    python3 1.5_MANE_filter_alignment.py ${MANE_protein_id}_orthologs.txt ${MANE_protein_id}_orthologs_protein_ids.txt ${MANE_protein_id}_species_names.txt

     # outputs sequence_w_introns.fasta
    ./2nd_Pipe_intron_pos.sh ${MANE_protein_id}_orthologs_protein_ids.txt

    mv sequence_w_introns.fa ${MANE_protein_id}_sequence_w_introns.fa

    /home/choh1/intron_pos_conserv/muscle5.1.linux_intel64 -align ${MANE_protein_id}_sequence_w_introns.fa -output ${MANE_protein_id}_aln_seq_w_introns.afa

    python3 2_MANE_reorder_alignment.py ${MANE_protein_id}_aln_seq_w_introns.afa reorder_aln_seq_w_introns.afa ${MANE_protein_id}

    python3 3_MANE_analyze_introns_species_name.py reorder_aln_seq_w_introns.afa ${MANE_protein_id}_intron_analysis.txt

    python3 4_MANE_extract_species_names_from_muscle_aln.py reorder_aln_seq_w_introns.afa ${MANE_protein_id}_species_names.txt
    /ccb/sw/bin/python3.6 4.6_MANE_build_common_taxonomy.py ${MANE_protein_id}_species_names.txt ${MANE_protein_id}_tree.nwk

    python3 5_MANE_make_color_annot.py ${MANE_protein_id}_intron_analysis.txt ${MANE_protein_id}

    mv ${MANE_protein_id}_* "${MANE_protein_id}/"

    echo "Completed processing MANE protein ${MANE_protein_id}"

done
