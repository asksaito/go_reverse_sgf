# coding:utf-8
import sys
import os
import codecs
import re

# Default board size
board_size = 19

def main():
    if len(sys.argv) <= 1:
        print("[ERROR] Input file not found. (SGF file required)")
        sys.exit(1)

    # Get input file path
    input_file_path= sys.argv[1]

    # Get input file dir and name
    input_file_dir = os.path.dirname(input_file_path)
    input_file_basename = os.path.basename(input_file_path)

    split_input_file_name = os.path.splitext(input_file_basename)
    input_file_name = split_input_file_name[0]
    input_file_ext = split_input_file_name[1]

    # Check extension
    if (input_file_ext.lower() != ".sgf"):
        print("[ERROR] Input file is not SGF format. ({})".format(input_file_basename))
        sys.exit(1)

    # Make output file path
    output_file_path = os.path.join(input_file_dir, input_file_name + "_reversed" + input_file_ext)

    # Detect input file encoding
    file_encoding = detect_encoding(input_file_path)
    print("file_encoding is {}".format(file_encoding))

    # Open input file (read only mode)
    with codecs.open(input_file_path, 'r', file_encoding) as input_file:
        # Open output file (write mode)
        with codecs.open(output_file_path, 'w', file_encoding) as output_file:
            # Read file line by line
            for line in input_file:
                # Update board_size if exist
                update_board_size(line)

                # Reverse setup stones (oki-ishi) if exist
                line = reverse_setup_stones(line)

                # Get all matched strings (;B[xx] or ;W[xx] or ;B[] or ;W[])
                bw_position_regex = r';[BW]\[[a-zA-Z]{0,2}\]' # 0 represents pass
                bw_position_list = re.findall(bw_position_regex, line)
                if not bw_position_list:
                    output_file.write(line)
                else:
                    # output string before ';B' or ';W'
                    output_file.write(line[:re.search(r';[BW]', line).start()])
                    
                    for bw_position in bw_position_list:
                        # Process ;B[xx] or ;W[xx] or ;B[] or ;W[] in order
                        position = re.search(r'\[([a-zA-Z]{0,2})\]', bw_position).group(1)

                        # Reverse coordinate
                        converted_position = reverse_coordinate(position)

                        coverted_bw_position = bw_position.replace(position, converted_position)

                        # output converted position
                        output_file.write(coverted_bw_position)
                    
                    # output string after last ;B[xx] or ;W[xx]
                    output_file.write(line[rfind_regex(bw_position_regex, line):])

    # Show result
    print("[COMPLETED] output_file -> " + output_file_path)

def update_board_size(line):
    global board_size

    sz = re.search(r'SZ\[(\d+)\]', line)
    if (sz != None):
        # 'SZ[nn]' is exist
        board_size = int(sz.group(1))
        print("board_size is {}".format(board_size))

def reverse_setup_stones(line):
    maches_setup_stones = re.search(r'AB(\[[a-zA-Z]{2}\])+', line)
    if (maches_setup_stones != None):
        # setup_stones = 'AB[xx][yy][zz]' is exist
        setup_stones = maches_setup_stones.group()

        setup_stone_list = re.findall(r'\[([a-zA-Z]{2})\]', setup_stones)

        converted_setup_stones = "AB"
        for setup_stone in setup_stone_list:
            reversed_setup_stones = reverse_coordinate(setup_stone)
            converted_setup_stones += "[{}]".format(reversed_setup_stones)
        
        print("setup_stones are reversed")
        # Return reverse setup stones line
        return line.replace(setup_stones, converted_setup_stones)
    
    # Return as line
    return line

def reverse_coordinate(position):
    # Make char to number dictionary
    letter_to_number = {
        'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8, 'i': 9, 'j': 10,
        'k': 11, 'l': 12, 'm': 13, 'n': 14, 'o': 15, 'p': 16, 'q': 17, 'r': 18, 's': 19
    }
    # Make number to char dictionary
    number_to_letter = {v: k for k, v in letter_to_number.items()}

    if not position:
        # Empty string
        return position

    # Reverse coordinate
    converted_position = ""
    for char in position.lower():
        converted_number = (board_size + 1) - letter_to_number[char]
        converted_position += number_to_letter[converted_number]
    
    return converted_position

def detect_encoding(file_path):
    # Use the first encoding that does not cause errors
    encodings_to_try = ['utf-8', 'sjis', 'ascii']
    for encoding in encodings_to_try:
        try:
            with codecs.open(file_path, 'r', encoding=encoding) as file:
                file.read()
            return encoding
        except UnicodeDecodeError:
            continue
    
    # Return default encoding
    return 'unknown'

def rfind_regex(pattern, text):
    last_match = None

    for match in re.finditer(pattern, text):
        last_match = match

    if last_match:
        return last_match.end()
    else:
        return -1

if __name__ == "__main__":
    main()
