import csv
import json
import urllib.request
import random
import sys

def get_random_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

def get_color(region_name):
    #Return black if region_name is Disordered and get_random_color() otherwise
    if region_name == 'Disordered':
        return '#000000'
    else:
        return get_random_color()

def read_names_from_fasta(input_fasta):
    names = []
    with open(input_fasta, mode='r') as file:
        for line in file:
            if line.startswith('>'):
                names.append(line[1:-1])
    return names

def extract_uniprot_id(name):
    return name.split('|')[1]

# Function to retrieve regions from UniProt API
def get_regions_uniprot(uniprot_id):
    UNIPROT_API_URL = "https://rest.uniprot.org/uniprotkb"
    url = f"{UNIPROT_API_URL}/{uniprot_id}.json"
    regions = []
    
    try:
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                uniprot_results = json.load(response)
                for feature in uniprot_results['features']:
                    if feature['type'] in ('Region', 'Motif', 'Domain', 'Compositional bias', 'DNA binding', 'Zinc finger','Transmembrane', 
                                           'Intramembrane', 'Coiled coil', 'Disordered', 'Repeat', 'Coiled coil',
                                           'Active site', 'Binding site'):
                        name = feature['description']
                        color = get_color(name)
                        source = feature.get('evidences', [{}])[0].get('source', '')
                        sourceId = feature.get('evidences', [{}])[0].get('id', '')

                        if feature['type'] == 'Binding site' and not name:
                            if 'ligand' in feature:
                                if 'name' in feature['ligand']:
                                    name = f"{feature['type']} of {feature['ligand']['name']}"

                        regions.append({
                            'uniprot_id': uniprot_id,
                            'name': name,
                            'start': feature['location']['start']['value'],
                            'end': feature['location']['end']['value'],
                            'color': color,
                            'source': source,
                            'sourceId': sourceId
                        })
    except Exception as e:
        print(f"Error retrieving data for {uniprot_id}: {e}")
        raise e
    
    return regions

def get_regions_interpro(uniprot_id):
    # INTERPRO_API_URL = "https://www.ebi.ac.uk/interpro/api/entry/all/protein/reviewed/"
    INTERPRO_API_URL = "https://www.ebi.ac.uk/interpro/api/entry/interpro/protein/uniprot/"

    url = f"{INTERPRO_API_URL}{uniprot_id}"
    regions = []
    
    try:
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                interpro_results = json.load(response)
                for interpro_entry in interpro_results['results']:
                    name = interpro_entry['metadata']['name']
                    color = get_color(name)
                    if name:
                        for protein in interpro_entry['proteins']:
                            for location in protein['entry_protein_locations']:
                                for fragment in location['fragments']:
                                    regions.append({
                                        'proteinId': uniprot_id,
                                        'name': name,
                                        'start': fragment['start'],
                                        'end': fragment['end'],
                                        'color': color,
                                        'source': interpro_entry['metadata']['source_database'],
                                        'sourceId': interpro_entry['metadata']['accession']
                                    })

        INTERPRO_API_URL_EXTRA_FEATURES = f"https://www.ebi.ac.uk/interpro/api/protein/uniprot/{uniprot_id}?extra_features"

        with urllib.request.urlopen(INTERPRO_API_URL_EXTRA_FEATURES) as response:
            if response.status == 200:
                interpro_results = json.load(response)
                for name, feature in interpro_results.items():
                    if name == 'mobidb-lite':
                        name = 'Disordered'
                    color = get_color(name)
                    for location in feature['locations']:
                        for fragment in location['fragments']:
                            regions.append({
                                'proteinId': uniprot_id,
                                'name': name,
                                'start': fragment['start'],
                                'end': fragment['end'],
                                'color': color,
                                'source': feature['source_database'],
                                'sourceId': feature['accession']
                            })

            

    except Exception as e:
        print(f"Error retrieving data for {uniprot_id}: {e}")
        raise e
    
    return regions

def get_regions(uniprot_id, databases='uniprot'):
    # Mapping of database names to their corresponding functions
    database_functions = {
        'uniprot': get_regions_uniprot,
        'interpro': get_regions_interpro,
        # Add more databases and their functions here
    }

    regions = []
    for database in databases:
        if database in database_functions:
            regions.extend(database_functions[database](uniprot_id))
        else:
            print(f"Unknown database: {database}")
    return regions

def get_regions2(uniprot_id):
    regions = []
    new_regions = get_regions_interpro(uniprot_id)
    if not new_regions:
        new_regions = get_regions_uniprot(uniprot_id)

    regions.extend(new_regions)

    return regions

def main():
    if '--test' in sys.argv:
        #All kind of edge cases
        names = [
                'sp|Q13765|NACA',
                'sp|I4EPC4|HA',
                'sp|P61956|SUMO2',
                'sp|O14979|HNRNPDL',
                'sp|A0A2Z5U3Y8|M1',
                'sp|A6NMY6|ANXA2P2',
                'sp|A0A2Z5U3Y7|PA'
                ]
    else:
        input_fasta = sys.argv[1]
        names = read_names_from_fasta(input_fasta)

    # Prepare CSV writer
    sys.stdout.reconfigure(encoding='utf-8')
    csv_writer = csv.writer(sys.stdout, delimiter=',', quoting=csv.QUOTE_NONE, escapechar='\\')
    csv_writer.writerow(['ProteinId', 'AnnotName', 'StartRes', 'EndRes', 'Color', 'Source', 'SourceId'])

    # Retrieve regions and print to stdout
    for name in names:
        # print(name.split('|')[1])
        uniprot_id = extract_uniprot_id(name)
        regions = get_regions(uniprot_id, databases=['interpro'])
        regions.extend(get_regions(uniprot_id, databases=['uniprot']))
        # regions = get_regions2(uniprot_id)
        added = {}
        for region in regions:
            if region['name'] in added:
                color = added[region['name']]
            else:
                color = get_color(region['name'])
            row = [name, region['name'], region['start'], region['end'], color, region['source'], region['sourceId']]
            csv_writer.writerow(row)
            added[region['name']] = color

if __name__ == "__main__":
    main()
