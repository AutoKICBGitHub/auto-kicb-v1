input_file = "localization_merged.txt"  # Имя исходного файла
output_file = "localization_merged1.txt"  # Имя файла с заменёнными символами

old_char = "»"  # Какой символ заменить
new_char = "\""  # На что заменить


with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", encoding="utf-8") as outfile:
    for line in infile:
        outfile.write(line.replace(old_char, new_char))