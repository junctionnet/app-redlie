import base64
import os
import re

import pandas as pd


def clean_csv_remove_blanks(file_path, cleaned_file_path, data=None):
    # Read the entire file into memory
    try:
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = file.readlines()
        print("Encoding utf-8")
    except Exception:
        if file_path:
            with open(file_path, 'r', encoding='latin-1') as file:
                data = file.readlines()
        print("Encoding latin-1")
    # Remove all blank spaces from each line
    # print(data)
    char_replace = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', "ñ": "n", "ü": "u", ".": "", "-": "", "¿": ""}
    cleaned_data = []
    i=0
    for line in data:
        line = line.lower() #.rstrip(",\n")
        if i == 0:
            line = line.rstrip(",\n")
            line = line + "\n"
        i += 1
        # line = line + "\n"
        for old_char, new_char in char_replace.items():
            line = line.replace(old_char, new_char)
        cleaned_data.append(line)
    print("lines: ", i)
    print(f"Data after special character replace  {cleaned_data[:10]}")
    with open(cleaned_file_path, 'w', encoding='latin-1') as file:
        file.writelines(cleaned_data)

    return cleaned_file_path


def parse_multipart_formdata(raw_data, boundary):
    print("Boundary: ", boundary)
    raw_data = raw_data.replace("\r\n", "\n")
    print("Raw Data: ", raw_data)
    # Regular expression pattern to extract field names and values
    # form_pattern = r'name="([^"]+)"(?:; filename="([^"]+)")?(?:\nContent-Type: [^\n]+)?\n([\s\S]*?)(?=\n------WebKitFormBoundary|$)'
    form_pattern = r'name="([^"]+)"(?:; filename="([^"]+)")?(?:\nContent-Type: [^\n]+)?\n([\s\S]*?)(?=\n' + boundary + '|$)'
    # Extract matches
    matches = re.findall(form_pattern, raw_data)
    print("Matches: ", matches)

    # Dictionary to store parsed data
    form_data = {}
    print(form_data)

    file_name = None
    file_content = None

    for name, filename, value in matches:
        name = name.strip()
        value = value.strip()

        if filename:  # If there's a filename, it's the file field
            file_name = filename
            file_content = value
        else:
            form_data[name] = value

    # Return the structured data
    estudio = form_data.get('estudio', '')
    ubicacion = form_data.get('ubicacion', '')
    informantes = form_data.get('informantes', '')
    nivel_escolar = form_data.get('nivelEscolar', '')
    rol_informante = form_data.get('rolInformante', '')
    filename = form_data.get('filename', '')

    return {
        'filename': f"{estudio}-{ubicacion}-{informantes}-{nivel_escolar}-{rol_informante}-{filename}",
        'file_content': file_content,
        'estudio': estudio,
        'ubicacion': ubicacion,
        'informantes': informantes,
        'nivel_escolar': nivel_escolar,
        'rol_informante': rol_informante
    }


def parse_multipart_data(event_body, boundary):
    parts = event_body.split(boundary)
    file_content = None
    file_name = None
    estudio = None
    ubicacion = None
    informantes = None
    nivel_escolar = None
    rol_informante = None
    for part in parts:
        if "Content-Disposition" in part:

            if "form-data" in part:
                print("Part: ", part[:100])

                estudio = part.split('estudio="')[1].split('"')[0]
                ubicacion = part.split('ubicacion="')[1].split('"')[0]
                informantes = part.split('informantes="')[1].split('"')[0]
                nivel_escolar = part.split('nivelEscolar="')[1].split('"')[0]
                rol_informante = part.split('rolInformante="')[1].split('"')[0]

                if "filename" in part:
                    file_name = part.split('filename="')[1]
                    file_name = file_name.split('.csv"', 1)[0]
                    file_content = part.split("\r\n\r\n")[1].rstrip("\r\n--")

    return {
        'filename': file_name,
        'file_content': file_content,
        'estudio': estudio,
        'ubicacion': ubicacion,
        'informantes': informantes,
        'nivel_escolar': nivel_escolar,
        'rol_informante': rol_informante
    }


def decoded_body(body, is_base64_encoded=False):
    if is_base64_encoded and body:
        try:
            return base64.b64decode(body.encode()).decode('latin-1')
        except:
            return base64.b64decode(body.encode()).decode('latin-1', errors='ignore')
    return body


def encode_body(string_body):
    # Convert the input string to bytes
    try:
        byte_data = string_body.encode('utf-8')
        print(f"Encoded string: {string_body}")
    except UnicodeEncodeError:
        print(f"Error ignore encoding string: {string_body}")
        byte_data = string_body.encode('utf-8', errors='ignore')

    # Decode the base64 encoded bytes
    binary_data = base64.b64decode(byte_data)

    return binary_data


def fetch_request_body_file(body, boundary):
    string_decoded_body = body

    parts = string_decoded_body.split(boundary)

    request_body = {
        'filename': None,
        'file_content': None
    }

    for part in parts:

        if 'Content-Disposition' not in part:
            continue

        content_disposition = part.split(f'Content-Disposition:')[1].strip()
        print("Content-Disposition: ", content_disposition[:50])
        print("Part: ", part[:50])

        if request_body.get('filename') is None and "filename" in part:
            extension = '.xlsx' if '.xlsx' in content_disposition else (
                '.XLSX' if '.XLSX' in content_disposition else None)
            request_body['filename'] = content_disposition.split(f'filename=')[1].strip('"').split(extension)[
                                           0] + '.xlsx'
            request_body['file_content'] = part.split("\r\n\r\n")[1].rstrip("\r\n--")
            print("=" * 88)
            print("=====> File Name: ", request_body['filename'])
            print("=" * 88)
            continue

    request_body = {
        'filename': request_body['filename'],
        'file_content': request_body['file_content']
    }

    return request_body


def find_xlsx_files(directory):
    """Find all xlsx files in a given directory and its subdirectories."""
    xlsx_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".xlsx"):
                xlsx_files.append(os.path.join(root, file))
    return xlsx_files


def read_excel_and_filter(columns_of_interest, skiprows, uploaded_file):
    df = pd.read_excel(uploaded_file, skiprows=skiprows, engine='openpyxl')
    # Select only the columns of interest
    selected_df = df.filter(items=columns_of_interest)
    # Drop rows with all NaN values
    selected_df.dropna(how='all', inplace=True)
    # Reset index after dropping rows
    selected_df.reset_index(drop=True, inplace=True)
    # Display the resulting DataFrame
    # Print each line of data
    for index, row in selected_df.iterrows():
        print("Line", index + 1)
        for col in selected_df.columns:
            print(f"{col}: {row[col]}")
            if str(row[col]).lower() == 'nan' or str(row[col]).lower() == 'none':
                selected_df.at[index, col] = None
                if col == 'weight' or col == 'last_price':
                    selected_df.at[index, col] = 0.0

                print(f"{col}: {row[col]}")
        print("\n")  # Add a new line between each row
    records = selected_df.to_dict(orient='records')
    return records


def skiprows_read_excel_and_filter(uploaded_file, columns_of_interest):
    skiprows = 0
    # Maximum limit for skiprows
    max_skiprows = 11
    # Try reading the Excel file with increasing values of skiprows
    records = None
    while skiprows <= max_skiprows:

        records = read_excel_and_filter(columns_of_interest, skiprows, uploaded_file)

        if records:
            print("Records extracted successfully with skiprows:", skiprows)
            break
        else:
            print(f"No records extracted with skiprows {skiprows}. Trying with skiprows {skiprows + 1}.")
            skiprows += 1
    # logger.info(f"Catalog Extracted:  {len(records)}", extra={"count": len(records)})
    # print(f"Catalog Extracted:  {len(records)}")
    return records


class XlsxDocumentsLocalImport:
    def __init__(self, file_path, import_settings=None):
        self.import_settings = import_settings
        self.records = self._handle_path(file_path)

    def _process(self, file_path):
        print(f"Processing xlsx file: {file_path}")
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                content = file.read()

                self.import_settings['filename'] = os.path.basename(file_path)
                self.import_settings['file_content'] = content

                document_records = skiprows_read_excel_and_filter(file.name,
                                                                  self.import_settings.get('columns_of_interest'))
                return document_records
        except Exception as e:
            print(f"Failed to read {file_path}: {e}")

    def _handle_path(self, path):
        if os.path.isfile(path):
            if path.lower().endswith('.xlsx'):
                return self._process(path)
            else:
                print(f"The file {path} is not an xlsx file.")
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.lower().endswith('.xlsx'):
                        return self._process(os.path.join(root, file))
        else:
            print(f"The path {path} is neither a file nor a directory.")
