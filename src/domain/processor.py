from pathlib import Path

import pandas as pd

from src.services.records import Records
from src.utils import csv_document


def process_document(self, filename):
    file_path = Path('/tmp/uploaded_file.csv')
    try:
        file_path = file_path.with_name(filename)
    except KeyError as e:
        self.logger.error("Unable to get file name")

    cleaned_file_path = Path('/tmp/cleaned_bd.csv')

    file_path = self.documents_repository.download(file_path, filename)
    cleaned_file_path = csv_document.clean_up_document(file_path, cleaned_file_path)

    data = pd.read_csv(cleaned_file_path, delimiter=';', header=0)
    data = data[data.columns[0:5]]
    data.columns = ['NI', 'CI', 'EDAD', 'SEXO', 'VOCABLOS']

    self.logger.info(f"Data Columns: {str(data.columns)}")

    data_male = data[data['SEXO'] == 1]
    data_female = data[data['SEXO'] == 2]
    data_non_response = data[data['SEXO'] == 0]
    records = data.to_dict(orient='records')
    records_male = data_male.to_dict(orient='records')
    records_female = data_female.to_dict(orient='records')
    records_non_response = data_non_response.to_dict(orient='records')

    file_dict = {"file_name": filename, "entries": data.size,
                 "gender_data": {"male": data_male.size, "female": data_female.size,
                                 "non_answer": data_non_response.size}}
    self.logger.info(f"Processing pyload: {file_dict}")

    clear_records = csv_document.clear_data(records, "general")
    clear_records_male = csv_document.clear_data(records_male, "male")
    clear_records_female = csv_document.clear_data(records_female, "female")
    clear_records_non_response = csv_document.clear_data(records_non_response, "non-response")
    self.logger.debug(f"Records: {str(clear_records[:5])}")
    # Display the first few rows to verify the correct parsing
    _records = Records(clear_records, "general")
    _records_male = Records(clear_records_male, "male")
    _records_female = Records(clear_records_female, "female")
    _records_non_response = Records(clear_records_non_response, "non-response")

    stats = {"general": _records.stats, "male": _records_male.stats, "female": _records_female.stats,
             "non-response": _records_non_response.stats}
    self.logger.info(f"Records Stats: {stats}")
    # Getting words stats
    records_list = [_records, _records_male, _records_female, _records_non_response]
    words_stats = {"general": None, "male": None, "female": None, "non-response": None}
    for idx, record in enumerate(records_list):
        gender = list(words_stats.keys())[idx]
        words = {}
        for ci in range(1, len(record.ci_words.keys()) + 1):
            words[ci] = record.ci_words2[int(ci) - 1]["total"]
        words_stats[gender] = words

    self.logger.info(f"Words stats {words_stats}")

    _records.__dict__["disp1"] = _records_male.disp
    _records.__dict__["disp2"] = _records_female.disp
    _records.__dict__["disp3"] = _records_non_response.disp
    # elastic_repository.send_results(filename, _records.__dict__)
    self.logger.info("Results sent to elastic")
    return _records
