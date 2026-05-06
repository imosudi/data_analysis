"""
Generate PDF version of the analysis summary from Markdown.
"""

import os
from pathlib import Path
from markdown import markdown
from weasyprint import HTML, CSS

def markdown_to_html(md_file):
    """Convert Markdown file to HTML."""
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown(md_content, extensions=['extra', 'codehilite'])
    
    # Wrap in HTML structure with styling
    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Winter Tourism Data Analysis</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 900px;
                margin: 0 auto;
                padding: 40px;
                background-color: #f9f9f9;
            }}
            h1 {{
                color: #1f4788;
                border-bottom: 3px solid #0066cc;
                padding-bottom: 10px;
                font-size: 28px;
            }}
            h2 {{
                color: #0066cc;
                margin-top: 30px;
                font-size: 22px;
            }}
            h3 {{
                color: #0099ff;
                font-size: 18px;
            }}
            strong {{
                color: #1f4788;
            }}
            ul {{
                margin: 15px 0;
            }}
            li {{
                margin: 8px 0;
            }}
            code {{
                background-color: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }}
            img {{
                max-width: 100%;
                height: auto;
                margin: 20px 0;
                border: 1px solid #ddd;
                border-radius: 4px;
            }}
            a {{
                color: #0066cc;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            .footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                font-style: italic;
                color: #666;
            }}
            @page {{
                size: A4;
                margin: 2cm;
            }}
        </style>
    </head>
    <body>
        {html_content}
        <div class="footer">
            <p>Generated on 2026-05-06 | FH Technikum Wien Data Analysis Project</p>
        </div>
    </body>
    </html>
    """
    
    return full_html

def generate_pdf(md_file, output_file):
    """Generate PDF from Markdown file."""
    html_content = markdown_to_html(md_file)
    
    # Create PDF from HTML
    HTML(string=html_content).write_pdf(output_file)
    print(f"PDF generated successfully: {output_file}")

if __name__ == "__main__":
    # Get the directory of this script
    script_dir = Path(__file__).parent
    
    # Input and output paths
    md_file = script_dir / "analysis_summary.md"
    pdf_file = script_dir / "analysis_summary.pdf"
    
    # Generate PDF
    if md_file.exists():
        try:
            generate_pdf(str(md_file), str(pdf_file))
        except ImportError:
            print("Error: Required packages not installed.")
            print("Install with: pip install markdown weasyprint")
    else:
        print(f"Markdown file not found: {md_file}")
