# AnnotationsApp
Scripts and a web app for annotating proteins

Qick and dirty. Do not use it unless you know what you are doing.

## Installation
```bash
git clone
cd AnnotationsApp
pip install flask
pip install requests
```

## Usage
1. Start the app 
    ```bash 
    python app.py
    ```
1. Open your browser and go to the URL displayed in the terminal.
1. Paste UniProt IDs in the text area and optionally upload custom or prior annotations, or previously saved AnnotationsApp session.
1. Click on the "Annotate" button.
1. Wait for the annotations to be displayed.
1. Follow the instructions to select and save annotations.
1. If you intend to use these annotations for xiNET, you may need to run:
    ```bash
    python AnnotationsApp/clean_annotations_for_xiNET.py annotations.csv > annotations_cleaned.csv
    ```
    as xiNET does not support some characters in the annotation names.
