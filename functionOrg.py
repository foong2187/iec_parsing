import csv
import sys
import os


def correct_function_name(file, line):
    # Housekeeping
    merged_lines = line.strip()  # Staring point

    # Parse until the end of the section
    for curLine in file:
        curLine = curLine.strip()
        if curLine == "":
            break
        merged_lines += " " + curLine[2:]

    return merged_lines


def correct_data_spillover(file, line):
    # Housekeeping
    merged_lines = line.strip()  # Staring point

    # Parse until the end of the section
    for curLine in file:
        curLine = curLine.strip()
        if curLine.startswith("* \\param"):
            merged_lines += "\n- " + curLine[8:].strip()
        elif curLine == "*" or curLine == "*/" or curLine == "":
            break
        else:
            merged_lines += " " + curLine[2:].strip()

    return merged_lines


def parse_file(inputFiles):
    # Housekeeping
    brief, params, return_type, return_value, notes = "", "", "", "", ""
    function_data = []

    # Parses through a file and iterates after reaching the function name before reseting
    with open(inputFiles, "r") as file:
        for line in file:
            line = line.strip()
            # Skip lines that don't matter
            if (
                line == ""
                or line == "/**"
                or line == "*"
                or line == "/*"
                or line == "/*"
                or line == "*/"
            ):
                continue

            if line.startswith("MmsValue"):  #### Edgecase ####
                # If we have collected data, add it to the list
                line = correct_function_name(file, line)
                full_function_name = line
                simple_function_name = line[line.find("_") + 1 : line.find("(")]

                if brief == "":
                    brief = "No documentation provided"
                    params = "Unknown"
                    return_value = "Unknown"
                if return_type == "void":
                    return_value = "(none, void)"

                function_data.append(
                    [
                        full_function_name,
                        return_type,
                        simple_function_name,
                        brief,
                        params,
                        return_value,
                        notes,
                    ]
                )

                # Clear buffers
                brief, params, return_type, return_value, notes = "", "", "", "", ""
                continue

            # Fill the function data depending on the information type
            elif line.startswith("LIB61850_API"):
                return_type = line[13:]
            elif line.startswith("* \\brief"):
                brief += correct_data_spillover(file, line)[8:] + "\n\n"
            elif line.startswith("* \\param"):
                params += "- " + correct_data_spillover(file, line)[8:] + "\n\n"
            elif line.startswith("* \\return"):
                return_value += correct_data_spillover(file, line)[3:]
            else:
                notes += "-  " + correct_data_spillover(file, line)[2:] + "\n\n"

    return function_data


def export_to_csv(data, output_file):
    with open(output_file, "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        # Write header row
        csv_writer.writerow(
            [
                "Full Name",
                "Retrun Type",
                "Name",
                "Description",
                "Params",
                "Return Value",
                "Notes",
            ]
        )

        # Write data rows
        for function in data:
            csv_writer.writerow(function)


def main():
    # Check if a parameter is given
    if len(sys.argv) != 2:
        print("Stop being a dummy and put in the file name")
        return

    input_file = sys.argv[1]

    # Check if the file exists
    if not os.path.exists(input_file):
        print(f"Stop being a dummy, the file '{input_file}' does not exist")
        return

    parsed_data = parse_file(input_file)

    # Export parsed data to CSV
    output_file = os.path.basename(input_file)
    export_to_csv(parsed_data, output_file)


if __name__ == "__main__":
    main()
