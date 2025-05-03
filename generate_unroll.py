import toml
import re
import csv
import sys
import shutil
import argparse




if __name__ == "__main__":
    # Your main code here

    def main():
    # Load the configuration file
        config = toml.load('config.toml')


    # Load the source code
        source_code_path = config['Unroll Locations']['source_file']
        backup_location = config['Unroll Locations']['backup_location']
        # Extract the file name from the source code path
        # Create a local copy of the source code

        # Parse command line arguments
        parser = argparse.ArgumentParser(description='Unroll loops and replace arrays in source code.')
        parser.add_argument('--unroll', action='store_true', help='Unroll loops in the source code')
        parser.add_argument('--replace-array', action='store_true', help='Replace arrays with direct values')
        parser.add_argument('--remove-simd', action='store_true', help='Remove SIMD instructions')
        parser.add_argument('--restore', action='store_true', help='Restore the source code from the backup')
        args = parser.parse_args()

        if(args.restore):

            shutil.copyfile(backup_location, source_code_path)
            sys.exit(0)


        # Check command line arguments
        unroll_loops = args.unroll
        replace_array = args.replace_array
        remove_simd = args.remove_simd


        shutil.copyfile(source_code_path, backup_location)

        with open(source_code_path, 'r') as file:
            source_code = file.read()
            # Extract the blocks of code
            start_block = re.search(r'//START(.*?)//START END', source_code, re.DOTALL).group(1)
            loop_block = re.search(r'//LOOP START(.*?)//LOOP END', source_code, re.DOTALL).group(1)
            end_block = re.search(r'//END(.*)', source_code, re.DOTALL).group(1)

        # Load the replacement table from the specified location
        replacement_table_path = config['Unroll Locations']['replacementtable_all_loops']
        all_but_first_loop_replacement = config['Unroll Locations']['replacementtable_all_but_first_loop']
        replacement_array = config["Unroll Locations"]["array_replacement_table"]
        smlad_table = config["Unroll Locations"]["array_replacement_table_smlad"]
        loop_count = config['unrolled_function']['loop_count']
        header = config['MCUNet-locations']['header_file']
        layer = config['unrolled_function']['layer']


        # Open the header file and extract the weights
        with open(header, 'r') as header_file:
            weights = r'weight{number}\[\d+\] = \{{.*?\}}'.format(number=layer)

            weights_line = re.search(weights, header_file.read())
            if weights_line:
                hex_numbers = re.findall(r'0x[0-9A-Fa-f]+', weights_line.group(0))
                sign_extended_numbers = [int(num, 16) if int(num, 16) < 0x80 else int(num, 16) - 0x100 for num in hex_numbers]
                sign_extended_16_bit_numbers = [num if num >= 0 else num | 0xFF00 for num in sign_extended_numbers]
            else:
                print("No Matching weights found in header.")
                sys.exit(1)


        # Open the replacement table CSV
        with open(replacement_table_path, 'r') as file:
            replacement_table = list(csv.reader(file))

        # Open the SMLAD replacement table CSV
        with open(smlad_table, 'r') as file:
            smlad_table = list(csv.reader(file))

        # Open the all but first loop replacement CSV
        with open(all_but_first_loop_replacement, 'r') as file:
            all_but_first_loop_replacement_table = list(csv.reader(file))

        # Open the array replacement table CSV
        with open(replacement_array, 'r') as file:
            array_replacement_table = [row for row in csv.reader(file)]

        final_code = start_block



        if remove_simd:
            for row in smlad_table:
                for i in range(int(row[0])):
                    loop_block = loop_block.replace(row[1].format(i=i), row[2].format(i=i)) #TODO: this does not recognize {i + 8} as a valid format


        hex_numbers_formatted = [f"{num & 0xFFFF:04X}" for num in sign_extended_16_bit_numbers]

        if unroll_loops:
            for i in range (loop_count):
                modified_loop = loop_block
                if i != 0:
                    for row in all_but_first_loop_replacement_table:
                        modified_loop = re.sub(row[0], row[1], modified_loop)
                for row in replacement_table:
                    modified_loop = modified_loop.replace(row[0], row[1])

                if replace_array:
                    for row in array_replacement_table:
                        for j in range(int(row[0])):

                            matches = re.findall(r'\{numbers\[.+?\]\}', row[2]) #finds all occurences of {numbers[i]} in the replacement string
                            new_val = row[2]

                            for match in matches:
                                to_be_evals = re.findall(r'\[(.*?)\]', match)[0]
                                evals = eval(to_be_evals)
                                new_val = new_val.replace(to_be_evals, str(evals))

                            modified_loop = modified_loop.replace(row[1].format(j=j), new_val)




                    modified_loop = modified_loop.format(numbers=hex_numbers_formatted)

                final_code += modified_loop
        else:
            final_code += loop_block


        final_code += end_block
        output_path = source_code_path #TODO: This is supposed to be the original file in the project
        with open(output_path, 'w') as output_file:
            output_file.write(final_code)
        print("done!")



    # Load the replace all loop




    pass

main()