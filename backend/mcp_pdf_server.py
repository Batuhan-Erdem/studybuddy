import os
import sys
import pdfplumber
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("PDF-Specialist")

@mcp.tool()
def read_pdf_content(file_path: str) -> str:
    """
    Reads a PDF file and returns its text content in a structured format.
    Args:
        file_path: The absolute path to the PDF file.
    """
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"

    try:
        sys.stderr.write(f"DEBUG: Opening PDF: {file_path}\n")
        text_content = []
        with pdfplumber.open(file_path) as pdf:
            sys.stderr.write(f"DEBUG: PDF opened. Total pages: {len(pdf.pages)}\n")
            for i, page in enumerate(pdf.pages):
                sys.stderr.write(f"DEBUG: Processing page {i+1}...\n")
                page_text = page.extract_text()
                if page_text:
                    text_content.append(f"--- Page {i+1} ---\n{page_text.strip()}")
                
                # Check for tables
                tables = page.extract_tables()
                if tables:
                    sys.stderr.write(f"DEBUG: Found {len(tables)} tables on page {i+1}\n")
                    for j, table in enumerate(tables):
                        text_content.append(f"\n[Table {j+1} on Page {i+1}]\n")
                        for row in table:
                            row_str = " | ".join([str(item) if item is not None else "" for item in row])
                            text_content.append(row_str)
        
        sys.stderr.write("DEBUG: PDF processing complete.\n")
        return "\n".join(text_content)
    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")
        return f"Error processing PDF: {str(e)}"


if __name__ == "__main__":
    mcp.run()
