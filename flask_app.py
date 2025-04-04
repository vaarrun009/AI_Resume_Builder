from flask import Flask, render_template, request, send_file, jsonify, url_for
import os
import base64
import tempfile
from google import genai
from pathlib import Path
import subprocess
import sys
import importlib.util
from flask import session

app = Flask(__name__)
# app.config['SECRET_KEY'] = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = 'temp_files'
app.config['PDF_FOLDER'] = 'pdf_files'

# Create the upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PDF_FOLDER'], exist_ok=True)

# Initialize the Gemini client
client = genai.Client(api_key='')

# Check if playwright is installed
def is_package_installed(package_name):
    return importlib.util.find_spec(package_name) is not None

# Function to generate resume content using Gemini 2.0
def generate_resume_content(fields, style_modifier=""):
    # Define required and optional fields
    optional_fields = {
        'languages': fields.get('languages', ''),
        'certifications': fields.get('certifications', ''),
        'hobbies': fields.get('hobbies', ''),
        'projects': fields.get('projects', '')
    }
    
    # Only include optional fields that are not empty
    optional_content = ""
    for field_name, field_value in optional_fields.items():
        if field_value.strip():
            optional_content += f"- {field_name.title()}: {field_value}\n"
    
    prompt = f"""
Generate a professionally designed, 1-2 paged ATS-optimized HTML resume based on the following information:

CANDIDATE DETAILS:
- Full Name: {fields.get('name','')}
- Target Role: {fields.get('role','')}
- Email: {fields.get('email','')}
- Phone: {fields.get('phone','')}
- Location: {fields.get('location','')}
- LinkedIn URL: {fields.get('linkedin','')}
- GitHub URL: {fields.get('github','')}

PROFESSIONAL CONTENT:
- Professional Summary: {fields.get('summary','')}
- Work Experience: {fields.get('experience','')}
- Education: {fields.get('education','')}
- Technical & Professional Skills: {fields.get('skills','')}

OPTIONAL CONTENT:
{optional_content}

DESIGN REQUIREMENTS:
1. Create a clean, modern design with minimal whitespace
2. Ensure proper semantic HTML structure for optimal ATS parsing
3. Use a single-column layout for better ATS compatibility
4. Include internal CSS only (no external dependencies)
5. Implement responsive design for digital viewing
6. Ensure print-friendly formatting with appropriate page breaks
7. Use standard, professional font families (Arial, Calibri, Georgia)
8. Maintain appropriate contrast ratios for accessibility
9. Include proper heading hierarchy (h1-h3) for section titles
10. Make the candidate's name prominently displayed with a font size of 30-32px
11. Use compact spacing with small margins and padding
12. Use smaller font sizes (11-12px for body text, 14-16px for headings)
13. Optimize for a 1-page resume when possible

OPTIMIZATION INSTRUCTIONS:
1. Strategically incorporate keywords from the target role throughout the resume
2. Format work experience with clear job titles, companies, dates, and bullet points
3. Quantify achievements with metrics and numbers when possible
4. Use action verbs to begin experience bullet points
5. Ensure consistent formatting for dates (MM/YYYY)
6. Organize skills into relevant categories that align with the target role
7. Avoid using tables, images, headers/footers, or text boxes that may confuse ATS
8. Include both the spelled-out and acronym versions of important industry terms
9. Create a filename-friendly title based on the candidate's name and target role
10. Use concise bullet points and efficient wording to maximize space

STYLING DETAILS:
1. The candidate's name should be in a larger font size (30-32px) at the top of the resume
2. Make sure to wrap the name in an element with class="name" or id="name"
3. Add appropriate CSS styles to emphasize the name

Format the final resume output as clean, properly indented HTML with embedded CSS.

IMPORTANT: Return ONLY raw HTML code without any code block formatting, markdown backticks, or explanatory text.
Do not include ```html or ``` markers in your response.

{style_modifier}
"""
    response = client.models.generate_content(
            model='gemini-2.0-flash-001',
            contents=prompt
        )
    
    html_content = response.text.strip()
    
    # Remove markdown code block markers if they exist
    if html_content.startswith("```html"):
        html_content = html_content[7:]  # Remove ```html from start
    elif html_content.startswith("```"):
        html_content = html_content[3:]  # Remove ``` from start
        
    if html_content.endswith("```"):
        html_content = html_content[:-3]  # Remove ``` from end
    
    # Also remove any lingering backticks or code block markers
    html_content = html_content.replace("```html", "").replace("```", "")

    return html_content

# Function to save HTML content to a file
def save_html_file(html_content, filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    return file_path

# Function to convert HTML to PDF using subprocess
def convert_html_to_pdf(html_path, pdf_path):
    try:
        python_executable = sys.executable
        result = subprocess.run(
            [python_executable, 'html_to_pdf.py', html_path, pdf_path],
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, f"Error: {e.stderr}"

# Helper function to parse the single text input into a dictionary of fields
def parse_input_text(text):
    fields = {}
    current_key = None
    current_value = []
    
    # Split the text into lines
    lines = text.splitlines()
    
    for line in lines:
        line = line.strip()
        # Skip empty lines
        if not line:
            continue
            
        # Detect section headers to ignore
        if line.startswith('#'):
            continue
            
        # Check if this line has a key-value pair
        if ":" in line and not line.startswith('-'):
            # If we were collecting values for a previous key, store them
            if current_key and current_value:
                fields[current_key] = '\n'.join(current_value)
                current_value = []
                
            # Extract the new key-value pair
            key, value = line.split(":", 1)
            key = key.strip().lower()
            value = value.strip()
            
            # If the value is empty, start collecting multi-line content
            if value:
                fields[key] = value
                current_key = None
            else:
                current_key = key
                current_value = []
        
        # If we have a current key and this line doesn't define a new key, add it to the value
        elif current_key and line:
            # Add the line to the current value
            current_value.append(line)
    
    # Don't forget to add the last field if we were collecting one
    if current_key and current_value:
        fields[current_key] = '\n'.join(current_value)
    
    return fields

# Helper function to convert PDF file to base64 string
def pdf_to_base64(pdf_path):
    with open(pdf_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    return base64_pdf

@app.route('/')
def index():
    default_text = """
# Resume Builder - Enter Your Information

## Personal Information (Required)
role: Senior Data Scientist
name: John Doe
email: john.doe@example.com
phone: (123) 456-7890
location: New York, NY 10001
linkedin: https://www.linkedin.com/in/johndoe
github: https://github.com/johndoe

## Professional Summary (Required)
summary: 
Results-driven Data Scientist with 5+ years of experience in machine learning, statistical analysis, and data visualization. Proven track record of delivering actionable insights that drive business growth and operational efficiency. Expertise in Python, R, and SQL with a strong background in developing predictive models for diverse industry applications. Passionate about translating complex data into clear strategic recommendations.

## Work Experience (Required)
experience: 
DATA SCIENTIST | ABC ANALYTICS INC. | JAN 2020 - PRESENT
- Led the development of a customer churn prediction model that reduced churn by 15%
- Collaborated with cross-functional teams to implement data-driven solutions
- Built and deployed interactive dashboards using Tableau for executive decision-making

JUNIOR DATA ANALYST | XYZ TECH | MAR 2018 - DEC 2019
- Conducted exploratory data analysis to identify trends and patterns
- Automated reporting processes, saving 10 hours per week
- Assisted in the implementation of A/B testing frameworks

## Education (Required)
education: 
M.S. in Data Science | University of Data Analytics | 2018
- GPA: 3.8/4.0
- Relevant coursework: Advanced Machine Learning, Big Data Systems, Statistical Methods

B.S. in Computer Science | Tech University | 2016
- Minor in Statistics
- Graduated with honors

## Technical Skills (Required)
skills: 
- Programming: Python (Pandas, NumPy, Scikit-learn, TensorFlow), R, SQL
- Data Visualization: Tableau, Power BI, Matplotlib, Seaborn
- Machine Learning: Classification, Regression, Clustering, NLP, Deep Learning
- Big Data: Hadoop, Spark, AWS (S3, EC2, EMR)
- Tools: Git, Jupyter, Docker, JIRA

## Languages (Optional)
languages: 
- English (Native)
- Spanish (Professional Working Proficiency)
- Mandarin Chinese (Elementary Proficiency)

## Certifications (Optional)
certifications: 
- AWS Certified Machine Learning Specialty (2022)
- Microsoft Certified: Azure Data Scientist Associate (2021)
- IBM Data Science Professional Certificate (2020)

## Projects (Optional)
projects: 
PREDICTIVE CUSTOMER CHURN MODEL | PERSONAL PROJECT | 2021
- Developed an ML model achieving 92% accuracy in predicting customer churn
- Used Random Forest, XGBoost, and neural networks with feature engineering
- Deployed model via Flask API with Docker containerization

## Hobbies & Interests (Optional)
hobbies: 
- Competitive programming and hackathons
- Kaggle competitions
- Technical blogging on medium.com
- Mountain biking and rock climbing
"""
    
    playwright_installed = is_package_installed("playwright")
    
    return render_template(
        'index.html', 
        default_text=default_text,
        playwright_installed=playwright_installed
    )

@app.route('/generate_resumes', methods=['POST'])
def generate_resumes():
    user_input = request.form.get('resume_details', '')
    
    if not user_input.strip():
        return jsonify({'error': 'Please enter your resume details.'}), 400
    
    # Parse the user input
    fields = parse_input_text(user_input)
    
    # Check for required fields
    required_keys = ["role", "name", "email", "phone", "location", "linkedin", "github", "summary", "experience", "education", "skills"]
    missing_fields = [key for key in required_keys if key not in fields or not fields[key]]
    
    if missing_fields:
        return jsonify({
            'error': f'Please fill in the following required fields: {", ".join(missing_fields)}.'
        }), 400
    
    style_modifiers = [
        "Style: Modern minimalist design with blue accents. Use compact spacing with font-size: 11px for body text, 14px for headings, and minimal margins. Ensure clean, professional layout with efficient use of space.",
        
        "Style: Traditional layout with elegant fonts. Use font-size: 12px for body text, 16px for headings. Minimize whitespace between sections, use 0.3-0.4in margins, and 1.1 line spacing for optimal density.",
        
        "Style: Creative but professional design with bold section headers. Use font-size: 11-12px for body text, crisp spacing, and compact layout. Include subtle color accents while maintaining ATS compatibility."
    ]
    
    pdf_versions = {}  # To store version name and PDF file paths
    html_versions = {}  # To store version name and HTML file paths
    
    # Check if playwright is installed
    playwright_installed = is_package_installed("playwright")
    
    for idx, mod in enumerate(style_modifiers):
        version_name = f"Version {idx+1}"
        
        # Generate HTML content
        html_content = generate_resume_content(fields, style_modifier=mod)
        
        # Ensure the HTML is a complete document if needed
        if "<html" not in html_content.lower():
            html_content = f"<html><head><meta charset='UTF-8'><title>Resume</title></head><body>{html_content}</body></html>"
        
        # Create unique filenames for HTML and PDF for each version
        safe_name = fields.get("name", "resume").replace(' ', '_')
        html_filename = f"{safe_name}_Resume_{idx+1}.html"
        pdf_filename = f"{safe_name}_Resume_{idx+1}.pdf"
        
        # Save HTML file
        html_path = os.path.abspath(save_html_file(html_content, html_filename))
        html_versions[version_name] = html_path
        
        # Convert to PDF if playwright is installed
        if playwright_installed:
            pdf_path = os.path.abspath(os.path.join(app.config['PDF_FOLDER'], pdf_filename))
            success, message = convert_html_to_pdf(html_path, pdf_path)
            
            if success:
                pdf_versions[version_name] = pdf_path
                print(f"Added PDF path to dictionary: {version_name} -> {pdf_versions[version_name]}")
            else:
                print(f"Failed to convert HTML to PDF: {message}")
    
    # Store the file paths in the session for later access
    session['html_versions'] = html_versions
    session['pdf_versions'] = pdf_versions if playwright_installed else {}
    session['selected_version'] = 'Version 1'
    
    # Create preview data for the front-end
    preview_data = {}
    if playwright_installed and pdf_versions:
        for version, pdf_path in pdf_versions.items():
            preview_data[version] = {
                'type': 'pdf',
                'url': f'/preview_pdf/{version}'
            }
    else:
        for version, html_path in html_versions.items():
            preview_data[version] = {
                'type': 'html',
                'url': f'/preview_html/{version}'
            }
    
    return jsonify({
        'success': True,
        'message': 'Resumes generated successfully!',
        'versions': list(preview_data.keys()),
        'previews': preview_data,
        'session_id': 'temp'  # In a production app, you'd use a real session ID
    })

@app.route('/preview_pdf/<version>')
def preview_pdf(version):
    pdf_versions = session.get('pdf_versions', {})
    
    if version not in pdf_versions:
        return "PDF not found", 404
    
    pdf_path = pdf_versions[version]
    base64_pdf = pdf_to_base64(pdf_path)
    
    return jsonify({
        'base64_pdf': base64_pdf
    })

@app.route('/preview_html/<version>')
def preview_html(version):
    html_versions = session.get('html_versions', {})
    
    if version not in html_versions:
        return "HTML not found", 404
    
    html_path = html_versions[version]
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    return html_content

@app.route('/download/<file_type>/<version>')
def download_file(file_type, version):
    if file_type == 'pdf':
        pdf_versions = session.get('pdf_versions', {})
        if version not in pdf_versions:
            return "PDF not found", 404
        
        file_path = pdf_versions[version]
        return send_file(file_path, as_attachment=True)
    
    elif file_type == 'html':
        html_versions = session.get('html_versions', {})
        if version not in html_versions:
            return "HTML not found", 404
        
        file_path = html_versions[version]
        return send_file(file_path, as_attachment=True)
    
    return "Invalid file type", 400

if __name__ == '__main__':
    app.run(debug=True)
