# html_to_pdf.py
from playwright.sync_api import sync_playwright
import sys

def convert_html_to_pdf(html_path, pdf_path):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            
            # Create a page with a viewport size that matches standard paper
            page = browser.new_page(viewport={"width": 850, "height": 1100})
            
            # Navigate to the HTML file
            page.goto(f"file://{html_path}")
            
            # Wait for any potential fonts or resources to load
            page.wait_for_timeout(1000)
            
            # Add custom CSS to reduce whitespace and font sizes
            page.eval_on_selector('body', '''(body) => {
                // Create a style element
                const style = document.createElement('style');
                style.textContent = `
                    body {
                        font-size: 12px;
                        line-height: 1.2;
                        margin: 0;
                        padding: 0;
                    }
                    /* Make the name/header larger */
                    h1.name, 
                    .name,
                    .header h1, 
                    .resume-header h1,
                    header h1,
                    .candidate-name,
                    h1:first-of-type {
                        font-size: 32px !important;
                        font-weight: bold !important;
                        margin-bottom: 8px !important;
                        color: #333 !important;
                    }
                    h1 { font-size: 18px; margin: 6px 0; }
                    h2 { font-size: 16px; margin: 5px 0; }
                    h3 { font-size: 14px; margin: 4px 0; }
                    p { margin: 3px 0; }
                    ul, ol { margin: 3px 0; padding-left: 20px; }
                    li { margin: 2px 0; }
                    section, div { margin-bottom: 8px; }
                    .container, .content, .wrapper, .resume-container { 
                        margin: 0 !important;
                        padding: 0 !important;
                    }
                    /* Override any excessive margins and padding */
                    * {
                        max-margin-top: 10px !important;
                        max-margin-bottom: 10px !important;
                    }
                `;
                document.head.appendChild(style);
            }''')
            
            # Allow some time for the custom CSS to apply
            page.wait_for_timeout(500)
            
            # Print to PDF with letter size paper and tighter margins
            pdf_bytes = page.pdf(
                path=pdf_path,
                format="Letter",
                print_background=True,
                margin={
                    "top": "0.3in",
                    "right": "0.3in",
                    "bottom": "0.3in",
                    "left": "0.3in"
                },
                scale=0.95  # Slightly reduce scale to fit more content
            )
            
            browser.close()
            return True
    except Exception as e:
        print(f"Error converting HTML to PDF: {str(e)}", file=sys.stderr)
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python html_to_pdf.py <html_path> <pdf_path>", file=sys.stderr)
        sys.exit(1)
        
    html_path = sys.argv[1]
    pdf_path = sys.argv[2]
    
    success = convert_html_to_pdf(html_path, pdf_path)
    if success:
        print(f"Successfully converted {html_path} to {pdf_path}")
        sys.exit(0)
    else:
        sys.exit(1)