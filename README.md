# 🌌 **AI Resume Builder** ✨🧠

---

> _“Do the mundane, you must not._  
> _Built for greatness, you are.”_  
>  
> **The Force of AI, is with your resume** 🔮📄  
>  
> Begun, your job hunt has "Young Padawan" 👇👇👇

---

<p align="center">
  <img src="https://media.giphy.com/media/26tn8zNgVmit475RK/giphy.gif?cid=790b7611il327ayk9uoe9u20vnp02htaab8u4wnajtstcebt&ep=v1_gifs_search&rid=giphy.gif&ct=g" width="500" alt="Yoda AI Power GIF"/>
</p>

---




## Resume Builder Demo 🎬
https://github.com/user-attachments/assets/2b2d1bd9-6ebf-4668-9038-46e3ccb9276f


## Features 🚀

* **📝 Text Input:** Easily paste your existing resume details or write new ones.
* **🤖 AI-Powered Generation:** Automatically formats your input into structured resume data (or uses predefined logic). 
* **🎨 Multiple Templates:** Generates previews using several distinct visual templates.
* **👁️ Live Preview:** Instantly view the selected resume version within the app.
* **🖼️ Sleek UI:** Modern interface with glassmorphism effects, subtle animations, and a video background.
* **📄 HTML Download:** Download the currently previewed resume as an HTML file.
* **📜 PDF Download:** Download the resume as a PDF file (requires Playwright).
* **🔄 Responsive Design:** Adapts to different screen sizes (basic responsiveness included).

---

## Tech Stack 🛠️

* **Frontend:**
    * HTML5
    * CSS3 (Flexbox, Animations, Glassmorphism)
    * JavaScript (Vanilla JS, Fetch API, DOM Manipulation)
    * Font Awesome (Icons)
* **Backend:**
    * Python
    * Flask 
    * Jinja2 (Template Engine)
* **PDF Generation:**
    * Playwright
* **AI Component**
    * Gemini

---

## Setup & Installation ⚙️

Follow these steps to run the project locally:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/vaarrun009/AI_Resume_Builder.git
    cd AI_Resume_Builder
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Linux/macOS
    python3 -m venv venv
    source venv/bin/activate

    # Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install Python dependencies:**
    *(Make sure you have created a `requirements.txt` file first: `pip freeze > requirements.txt`)*
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install Playwright browsers:**
    *(Playwright library should be in requirements.txt)*
    ```bash
    playwright install
    ```
    *(This might take a few minutes as it downloads browser binaries)*

5.  **Place your background video:**
    * Ensure your `background.mp4` (or appropriately named video file) is located in the `static/` directory.

6.  **Run the application:**
    ```bash
    export FLASK_APP=flask_app.py # Linux/macOS
    export FLASK_ENV=development # Optional: enables debug mode

    # set FLASK_APP=flask_app.py # Windows (cmd)
    # $env:FLASK_APP = "flask_app.py" # Windows (PowerShell)
    # set FLASK_ENV=development # Windows

    flask run
    ```
    *(Alternatively, if your `flask_app.py` has `if __name__ == '__main__': app.run(...)`, you can just run `python flask_app.py`)*

7.  **Open your browser** and navigate to `http://127.0.0.1:5000` (or the address provided by Flask).

---

## Usage Guide 📖

1.  Navigate to the application URL in your web browser.
2.  Paste your complete resume details into the "Resume Details" text area.
3.  Click the "Generate Resume Previews" button.
4.  Wait for the previews to generate. The preview area will appear below.
5.  Select different template versions using the buttons provided above the preview frame.
6.  The preview frame will update to show the selected version.
7.  Click "Download HTML" or "Download PDF" to save the *currently selected* resume version.

---

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---
Crafted with ❤️ by vaarrun.
