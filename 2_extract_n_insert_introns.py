import sys

def determine_strand_orientation(genomic_intervals):
    strand_orientation = "positive" if genomic_intervals[0][0] < genomic_intervals[1][0] else "negative"
    return strand_orientation


def new_extract_aa_intron_positions(table_path):

    with open(table_path, 'r') as file:
        lines = file.readlines()

    if len(lines) < 4:
        raise ValueError("The input table file appears to be empty or improperly formatted.")
    
    coding_lengths = [int(line.split()[5]) for line in lines[2:] if len(line.split()) > 4]
    print("table coding len", coding_lengths)

    genomic_intervals = [list(map(int, line.split()[0].split('-'))) for line in lines[2:]]

    if len(genomic_intervals) < 1:
        raise ValueError("There should be at least two genomic intervals in the input table file.")

    # print("gene_intervals", genomic_intervals)
    # strand_orientation = determine_strand_orientation(genomic_intervals)

    # if strand_orientation == "positive":
       # coding_lengths = coding_lengths
    # else:
      #  coding_lengths.reverse()

    protein_coding_len = [round(x / 3) for x in coding_lengths]
    print("protein_coding_len", protein_coding_len)

    for i in range(1, len(protein_coding_len)):
        protein_coding_len[i] += protein_coding_len[i - 1]

    intron_pos = [x + 1 for x in protein_coding_len[:-1]]
    print("intron_positions", intron_pos)

    return intron_pos


def extract_aa_intron_positions(table_path):
    with open(table_path, 'r') as file:
        lines = file.readlines()

    if len(lines) < 4:
        raise ValueError("The input table file appears to be empty or improperly formatted.")

    genomic_intervals = [list(map(int, line.split()[0].split('-'))) for line in lines[2:]]
    
    if len(genomic_intervals) < 1:
        raise ValueError("There should be at least two genomic intervals in the input table file.")

    # print("gene_intervals", genomic_intervals)
    strand_orientation = determine_strand_orientation(genomic_intervals)

    if strand_orientation == "positive":
        genomic_intervals = sorted(genomic_intervals, key=lambda x: x[0])
    else:
        genomic_intervals = sorted(genomic_intervals, key=lambda x: x[1])
        genomic_intervals = [[end, start] for start, end in genomic_intervals]



    starting_position = genomic_intervals[0][0]
    # print("Starting pos", starting_position)
    new_genomic_intervals = [[start - starting_position, end - starting_position] for start, end in genomic_intervals]
    print("New_genomic_interval", new_genomic_intervals)
    # divided_genomic_intervals = [[round(start / 3), round(end / 3)] for start, end in new_genomic_intervals]
    exon_len_coding_len = [round((end - start)/3) for start, end in new_genomic_intervals]
    sum_previous = []
    current_sum = 0
    print("exon_len_coding_len", exon_len_coding_len[:-1])
    for length in exon_len_coding_len[:-1]:
        current_sum += length
        sum_previous.append(current_sum)

    intron_pos = [x + 1 for x in sum_previous]
    print("intron pos", intron_pos)
    return intron_pos

def insert_introns_into_sequence(sequence, intron_positions):
    sequence_with_introns = list(sequence)

    for pos in intron_positions:
        sequence_with_introns.insert(pos, 'X')

    return ''.join(sequence_with_introns)

def extract_amino_acid_sequence(file_content):
    lines = file_content.split('\n')
    sequence_lines = [line for line in lines if not line.startswith(">")]
    return "".join(sequence_lines)

def get_fasta_header(file_content):
    lines = file_content.split('\n')
    header_line = [line for line in lines if line.startswith(">")]
    return header_line[0] if header_line else ""

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python insert_introns.py <table.txt> <amino_acid_fasta.txt>')
        sys.exit(1)

    table_path = sys.argv[1]
    aa_fasta_path = sys.argv[2]
    aa_intron_positions = new_extract_aa_intron_positions(table_path)

    with open(aa_fasta_path, 'r') as f:
        file_content = f.read()

    fasta_header = get_fasta_header(file_content)
    amino_acid_sequence = extract_amino_acid_sequence(file_content)

    sequence_with_introns = insert_introns_into_sequence(amino_acid_sequence, aa_intron_positions)

    # print(fasta_header)
    # print(sequence_with_introns)
    # print(f"{fasta_header}\n{sequence_with_introns}")

    with open("sequence_w_introns.fa", 'a') as f:
        f.write(f"{fasta_header}\n")
        f.write(f"{sequence_with_introns}\n")

    # print(f"Sequence with introns saved to {output_file}")
