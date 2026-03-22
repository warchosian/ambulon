import os
from app.conversion.commands.md2html import process_markdown_to_html

# Define the input and output file paths
input_file = "doc/REGLES_PLANTUML.md"
output_dir = "C:/Users/herve.marchal/.gemini/tmp/f46b4f4e3c4f03feb1c5ba26a17e3d7d0e8982461efd263514fcb1d847a4756e"
output_file = os.path.join(output_dir, "REGLES_PLANTUML.html")

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Run the conversion
try:
    process_markdown_to_html(input_file, output_file, standalone=True, verbose=True)
    print(f"Successfully converted {input_file} to {output_file}")
except Exception as e:
    print(f"An error occurred: {e}")