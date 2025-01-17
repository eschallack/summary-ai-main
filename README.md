
# Synopsis AI - Help Guide

## Table of Contents
- [How to Install](#how-to-install)
- [Basic Usage](#basic-usage)

---

## How to Install

Follow these steps to set up the application:

### Step 1: Prerequisites
- Ensure [Python 3.12](https://www.python.org/downloads/windows/) and [Ollama](https://ollama.com/download/windows) are installed on your computer, along with llama3.2:latest.

### Step 2: Download the Code
- Download the repository and navigate to the project folder.

### Step 3: Set Up the Environment
1. Open a terminal in the project directory.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\scripts\activate
     ```
4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Step 4: Start the Program
Run the program using the following command:
```bash
python main.py
```

---

## Basic Usage

### Main Menu
After starting the program, you'll see a menu of options. Currently, the **Short Synopsis Generator** is the main working feature, offering:
1. **Single Synopsis**
2. **Bulk Synopsis Conversion**

To access the Short Synopsis menu, type `1`.

### Short Synopsis Generator

#### 1. Single Synopsis
- Paste the synopsis you want to shorten into the prompt.
- Specify the maximum character count (or press enter to use the default limit).
- Provide any helpful context about the episode/show. This could include:
  - **Genre**
  - **Show synopsis**
  - Example format:
    ```text
    genres: action and adventure, show_synopsis: the show about the thing that happened.
    ```

#### 2. Bulk Synopsis
##### Metadata Format
- Use the provided example template: `app/examples/short_synopsis_input_format_example.xlsx`
- Required fields:
  - `id`
  - `title`
  - `synopsis`
- Optional fields for additional context:
  - `genre`
  - `keywords`
  - `show_synopsis`

##### Usage
- Provide the path to your spreadsheet. Ensure:
  - The path has **no spaces** or is wrapped in **quotation marks**.
- Enter the maximum character length for the synopsis.
- The program will:
  - Iteratively refine the synopsis to meet the character limit while maintaining clarity.
  - Perform quality control to ensure the outputs are meaningful.
- Results are saved in a new file alongside the input spreadsheet.

---

If you encounter any issues, feel free to open an issue on the GitHub repository.
