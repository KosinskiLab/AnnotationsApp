
from flask import Flask, request, render_template, jsonify
import requests
import json
from get_annotations import get_regions
import csv

app = Flask(__name__)

def read_annotations_file(file):
    annotations = []
    if file and file.filename != '':
        # Use csv.DictReader to read the file as a dictionary
        csv_file = csv.DictReader(line.decode('utf-8') for line in file.stream)
        for row in csv_file:
            # Each row is now a dictionary with header row values as keys
            annotations.append(
                {
                    'proteinId': row['ProteinId'].split('|')[1],
                    'proteinShortName': row['ProteinId'].split('|')[2],
                    'start': int(row['StartRes']),
                    'end': int(row['EndRes']),
                    'name': row['AnnotName'],
                    'color': row['Color'],
                    'source': row['Source'],
                    'sourceId': row['SourceId']
                }
            )
    return annotations

@app.route('/')
def index():
    return render_template('index.html')

def upload_session(requesr):
    file = request.files['saved_session_file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    # Read the file content
    file_content = file.read()
    # Parse file content as JSON
    session_data = json.loads(file_content.decode('utf-8'))
    # Process the session data as needed
    # For example, return it as a response or save it to a database
    return session_data

@app.route('/annotate', methods=['POST'])
def annotate():
    custom_annotations = []
    if request.files['saved_session_file']:
        session_data = upload_session(request)
        protein_data = session_data.get('proteinData', [])
        custom_annotations = session_data.get('customAnnotations', [])
        prior_annotations = session_data.get('savedAnnotations', [])

    else:
        protein_ids = request.form['protein_ids'].split()
        databases = request.form.getlist('annotationDatabases')
        protein_data = []
        for protein_id in protein_ids:
            uniprot_url = f"https://www.uniprot.org/uniprot/{protein_id}.json"
            response = requests.get(uniprot_url)
            if response.status_code == 200:
                data = response.json()
                protein_length = data.get('sequence', {}).get('length', 0)
                short_name = data.get('uniProtkbId', '')
                gene_names = data.get('genes', [])
                if gene_names:
                    # Assuming primary gene name is the first one listed
                    primary_gene_name = gene_names[0].get('geneName', {}).get('value', 'N/A')
                if 'InterPro' in databases:
                    interpro_annotations = get_regions(protein_id, databases=['interpro'])
                else:
                    interpro_annotations = []
                if 'UniProt' in databases:
                    uniprot_annotations = get_regions(protein_id, databases=['uniprot'])
                else:
                    uniprot_annotations = []

                protein_data.append({
                    'id': protein_id,
                    'length': protein_length,
                    'short_name': primary_gene_name,  # Add the short name to the data dictionary
                    'uniprot_annotations': uniprot_annotations,
                    'interpro_annotations': interpro_annotations
                })

        prior_annotations = read_annotations_file(request.files['annotations_file'])
    
    custom_annotations.extend(read_annotations_file(request.files['custom_annotations_file'])) #TODO: put it more consistent with the other annotations in protein_data


    #For backward compatibility with sessions from older app versions
    #replace uniprot_id in annotations with sourceId
    for protein in protein_data:
        for annot in protein['uniprot_annotations']:
            if 'uniprot_id' in annot:
                annot['proteinId'] = annot.pop('uniprot_id')
    for protein in protein_data:
        for annot in protein['interpro_annotations']:
            if 'uniprot_id' in annot:
                annot['proteinId'] = annot.pop('uniprot_id')

    return render_template('annotate.html', protein_data=protein_data,
                           prior_annotations=prior_annotations, 
                           custom_annotations=custom_annotations)

if __name__ == '__main__':
    app.run(debug=True)
