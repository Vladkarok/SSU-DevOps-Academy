import os, sys, json

path_for_search = sys.argv[1]
files_list = os.listdir(path_for_search)

get_data = {}
result_info = []

with open(sys.argv[2], 'w') as create_result_file:

    for file_json in files_list:
        full_file_path = os.path.join(path_for_search, file_json)

        with open(full_file_path, 'r') as file_content:

            load_data = json.load(file_content)
            
            max_number = 0.0

            for elements in load_data['matrix']:

                if int(elements['result']) != 0 and float(elements['number']) >= float(max_number):

                    get_data['id'] = elements['id']
                    get_data['number'] = elements['number']
                    get_data['committer_name'] = elements['committer_name']
                    get_data['committer_email'] = elements['committer_email']

                    max_number = elements['number']
                    
        result_info.append(get_data.copy())

    json.dump(result_info, create_result_file, indent="\t", sort_keys=False)