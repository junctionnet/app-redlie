import os
from datetime import datetime
from pathlib import Path

import pandas as pd

from src import env_vars
from src.common.Service import DatabaseService
from src.common.handler import JunctionNetEventHandler
from src.models.Redlie import Vocablo


class MuestrasService(DatabaseService):

    def __init__(self, database, repository, s3_repository, event_bus, logger, metrics, tracer):
        super().__init__(database, repository, event_bus, logger, metrics, tracer)
        self.s3_repository = s3_repository
        self._csv_document = None
        self._processor = None
        self._vocablos = None

    @property
    def vocablos(self):
        return self._vocablos

    @vocablos.setter
    def vocablos(self, value):
        self._vocablos = value

    @property
    def processor(self):
        return self._processor

    @processor.setter
    def processor(self, value):
        self._processor = value

    @property
    def csv_document(self):
        return self._csv_document

    @csv_document.setter
    def csv_document(self, value):
        self._csv_document = value

    def find_muestra(self, muestra_id, serialize=None):
        with self.database.connect() as session:
            with session.begin():
                self.repository.session = session

                muestra = self.repository.find_user_muesta(muestra_id)
                file_name = f"{muestra_id}/indices.xlsx"
                presigned_url = self.s3_repository.generate_presigned_url(file_name)
                _r = muestra.to_dict() if serialize else muestra
                _r.update({"download_presigned_url": presigned_url})

                self.event_bus.publish("redlie.idl", "find_muestra", {"muestra_id": muestra_id, "username": self.username})
                return _r

    def delete_muestra(self, muestra_id):
        with self.database.connect() as session:
            with session.begin():
                self.repository.session = session
                muestra = self.repository.find_user_muesta(muestra_id)
                if not muestra:
                    print("Muestra Does not exists...", muestra_id)
                    return {"message": "Muestra not found"}
                self.repository.session.delete(muestra)

        self.event_bus.publish("redlie.idl", "MuestraDeleted", {"muestra_id": muestra_id, "username": self.username})

    def find_user_data(self, serialize=None):
        with self.database.connect() as session:
            with session.begin():
                self.repository.session = session
                user = self.repository.find_user(self.username)
                if not user:
                    print("User Does not exists...", self.username)
                    print("Creating user...", self.username)
                    user = self.repository.user_model.create(username=self.username, email="lala@lele.com")
                    self.repository.session.add(user)
                    print("User created...", self.username)
                    self.event_bus.publish("redlie.idl.find_user_data", "create_user", {"username": self.username})

                self.event_bus.publish("redlie.idl", "find_user_data", {"username": self.username})
                return user._to_dict() if serialize else user

    def upload(self, filedata, file_name):
        print(f"File data: {filedata}")
        file_content = filedata

        date_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        id = f"{self.username}/{date_time}"

        file_name = id + "/" + file_name
        print(f"File file_name: {file_name[:100]}...")

        local_path = f"/tmp/{file_name}"

        # Ensure the directory exists
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        self.logger.info("File content: " + file_content[:100] + "...")

        if file_content:
            # Write file content to a local file
            with open(local_path, "x", encoding="latin-1") as f:
                f.write(file_content)
            # Encode content for S3 upload
            encoded_content = file_content.encode("latin-1")
            self.s3_repository.upload(s3_key=file_name, file_content=encoded_content)
        else:
            self.logger.error("File content couldn't be parsed")


        self.event_bus.publish("redlie.idl", "MuestraUploaded", {"file_name": str(file_name),  "username": self.username, "id": id})
        return {"file_name": file_name, "local_path": local_path, "message": "File uploaded successfully"}


    def load_and_process_csv(self, cleaned_file_path):
        # Load the CSV file with a specified delimiter and include the header
        data = pd.read_csv(cleaned_file_path, delimiter=';', header=0)
        print(f"Columns in file: {data.columns}")  # Expected column names
        print(f"Total rows in file: {len(data)}")  # Expected row count

        # df_cleaned = data.dropna()  # If you're using dropna(), count again
        # print(f"Rows after cleaning: {len(df_cleaned)}")

        # Normalize column names to lowercase and strip spaces
        data.columns = data.columns.str.strip().str.lower()

        # Map required columns by their names
        column_mapping = {
            'ni': 'NI',
            'ci': 'CI',
            'edad': 'EDAD',
            'sexo': 'SEXO',
            'vocablos': 'VOCABLOS'
        }

        # Check if all required columns are present
        missing_columns = [col for col in column_mapping.keys() if col not in data.columns]
        print(missing_columns)
        print(data.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        # Rename columns using the mapping
        data = data.rename(columns={key: column_mapping[key] for key in column_mapping if key in data.columns})

        # Filter to include only the required columns
        data = data[list(column_mapping.values())]

        # Return the processed DataFrame
        return data

    def import_data(self, file_path):
        _dir = "." if env_vars.LOCAL else "/tmp"
        cleaned_file_path = Path(f"{_dir}/cleaned_bd.csv")
        cleaned_file_path = self.csv_document.clean_csv_remove_blanks(file_path, cleaned_file_path)
        data = self.load_and_process_csv(cleaned_file_path)

        with self.database.connect() as session:
            with session.begin():
                self.repository.session = session
                user = self.repository.find_user(self.username)
                if not user:
                    print("User Does not exists...", self.username)
                    print("Creating user...", self.username)
                    user = self.repository.user_model.create(username=self.username, email="lala@lele.com")
                    self.repository.session.add(user)
                    print("User created...", self.username)

                # Create a new muestra entry for the upload
                muestra = self.repository.muestra_model.create(user_id=user.id, file_name=file_path)
                self.repository.session.add(muestra)
                muestra_id = muestra.id
                self.repository.session.flush()  # Commit to get the ID of the muestra

        with self.database.connect() as session:
            with session.begin():
                self.repository.session = session
                muestra = self.repository.get_muesta(muestra_id)

                # Iterate through the DataFrame
                i = 1
                nis = []
                cis = []
                vocablos = []

                for _, row in data.iterrows():
                    edad_value = row.get('EDAD', 0)
                    edad = int(edad_value) if pd.notna(edad_value) else 0  # Ensure it's a valid integer

                    ni_value = row.get('NI', 0)
                    ni = int(ni_value) if pd.notna(ni_value) else 0  # Ensure it's a valid integer

                    ci_value = row.get('CI', 0)
                    ci = int(ci_value) if pd.notna(ci_value) else 0  # Ensure it's a valid integer

                    sexo_value = row.get('SEXO', 0)
                    sexo = int(sexo_value) if pd.notna(sexo_value) else 0  # Ensure it's a valid integer

                    vocablos_value = row.get('VOCABLOS', '') if pd.notna(
                        row.get('VOCABLOS', '')) else ''  # Ensure it's a valid string

                    # Add Participante entry
                    participante = self.repository.participante_model.create(
                        id=f"{muestra.id}-{i}",
                        muestra_id=muestra.id,
                        ni=ni,
                        ci=ci,
                        edad=edad,
                        sexo=sexo,
                        posicion=i
                    )
                    self.repository.session.add(participante)
                    # session.commit()  # Commit to get the ID of the participante

                    # Add Vocablos entrie
                    # print(f"Vocablos: {vocablos_value}")
                    for position, word in enumerate(vocablos_value.split(','), start=1):
                        vocablo = Vocablo(
                            id=f"{participante.id}-{position}",
                            participante_id=participante.id,
                            vocablo=word.strip(),
                            posicion=position
                        )
                        vocablos.append(vocablo)
                        self.repository.session.add(vocablo)

                    # Commit all changes
                    self.repository.session.flush()
                    i += 1
                    nis.append(ni)
                    cis.append(ci)

                    # print(f"Processed {i} records")
                nis = list(set(nis))
                cis = list(set(cis))
                vocablos = list(set(vocablos))
                muestra.update({
                    "participants_no": int(i),
                    "indices_no": len(vocablos),
                    "ni_no": len(nis),
                    "ci_no": len(cis)
                })
                print("Data successfully stored in the database.")
                print(f"Processed {i} records")
                self.repository.session.add(muestra)
                # self.repository.session.flush()
                muestra_id = muestra.id

        data = data[data.columns[0:5]]
        data.columns = ['NI', 'CI', 'EDAD', 'SEXO', 'VOCABLOS']

        data_male = data[data['SEXO'] == 1]
        data_female = data[data['SEXO'] == 2]
        data_non_response = data[data['SEXO'] == 0]
        records = data.to_dict(orient='records')
        records_male = data_male.to_dict(orient='records')
        records_female = data_female.to_dict(orient='records')
        records_non_response = data_non_response.to_dict(orient='records')

        file_dict = {"file_name": file_path, "entries": data.size,
                     "gender_data": {"male": data_male.size, "female": data_female.size,
                                     "non_answer": data_non_response.size}}

        # print(f"Processing pyload: {file_dict}")

        clear_records = self.vocablos.clear_data(records, "general")
        clear_records_male = self.vocablos.clear_data(records_male, "male")
        clear_records_female = self.vocablos.clear_data(records_female, "female")
        clear_records_non_response = self.vocablos.clear_data(records_non_response, "non-response")
        print(f"Records Male: {len(clear_records_male)}")
        print(f"Records Female: {len(clear_records_female)}")
        print(f"Records Non Response: {len(clear_records_non_response)}")
        print(f"Records General: {len(clear_records)}")

        # Display the first few rows to verify the correct parsing
        _records = self.vocablos.Records(clear_records, "general")
        _records_male = self.vocablos.Records(clear_records_male, "male")
        _records_female = self.vocablos.Records(clear_records_female, "female")
        _records_non_response = self.vocablos.Records(clear_records_non_response, "non-response")

        stats = {"general": _records.stats, "male": _records_male.stats, "female": _records_female.stats,
                 "non-response": _records_non_response.stats}
        print(f"Records Stats: {stats}")
        # Getting words stats

        records_list = [_records, _records_male, _records_female, _records_non_response]
        words_stats = {"general": None, "male": None, "female": None, "non-response": None}
        for idx, record in enumerate(records_list):
            gender = list(words_stats.keys())[idx]
            words = {}
            for ci in range(1, len(record.ci_words.keys()) + 1):
                _a = record.ci_words2[int(ci) - 1]
                print(f"Words: {_a}")

                words[ci] = record.ci_words2[int(ci) - 1]["total"]
                print(f"Words: {words[ci]}")
            words_stats[gender] = words

        print(f"Words stats {words_stats}")

        _records.__dict__["disp1"] = _records_male.disp
        _records.__dict__["disp2"] = _records_female.disp
        _records.__dict__["disp3"] = _records_non_response.disp

        with self.database.connect() as session:
            with session.begin():
                self.repository.session = session

                for ci_data in _records_male.disp:
                    for _w, _i in ci_data.get('values').items():
                        ci_indice = self.repository.indice_disponibilidad_model.create(
                            id=f"{muestra_id}-{ci_data.get('ci')}-{_w}-male",
                            muestra_id=muestra_id,
                            ci=ci_data.get('ci'),
                            sexo="male",
                            vocablo=_w,
                            indice=_i
                        )
                        print(f"CI Indice: {ci_indice.to_dict()}")
                        self.repository.session.add(ci_indice)
                    self.repository.session.flush()

                for ci_data in _records_female.disp:
                    for _w, _i in ci_data.get('values').items():
                        ci_indice = self.repository.indice_disponibilidad_model.create(
                            id=f"{muestra_id}-{ci_data.get('ci')}-{_w}-female",
                            muestra_id=muestra_id,
                            ci=ci_data.get('ci'),
                            sexo="female",
                            vocablo=_w,
                            indice=_i
                        )
                        print(f"CI Indice: {ci_indice.to_dict()}")
                        self.repository.session.add(ci_indice)
                self.repository.session.flush()
                for ci_data in _records_non_response.disp:
                    for _w, _i in ci_data.get('values').items():
                        ci_indice = self.repository.indice_disponibilidad_model.create(
                            id=f"{muestra_id}-{ci_data.get('ci')}-{_w}-non-response",
                            muestra_id=muestra_id,
                            ci=ci_data.get('ci'),
                            sexo="non-response",
                            vocablo=_w,
                            indice=_i
                        )
                        print(f"CI Indice: {ci_indice.to_dict()}")
                        self.repository.session.add(ci_indice)
                self.repository.session.flush()
        print("Results sent to elastic")
        print(_records.__dict__["disp1"])
        print(_records.__dict__["disp2"])
        print(_records.__dict__["disp3"])
        self.event_bus.publish("redlie.idl.process", "MuestraProcessed", {"muestra_id": muestra_id, "username": self.username, "participants_no": int(i),
                    "indices_no": len(vocablos),
                    "ni_no": len(nis),
                    "ci_no": len(cis)
                })
        return _records


if __name__ == "__main__":
    handler = JunctionNetEventHandler('Muestras')
    app_service = handler.service_factory.build()
    app_service.email = "test@test.test"
    app_service.username = "test"

    records = app_service.import_data("/Users/hector/code/junctionnet/github/redlie-api/tests/files/UNO.csv")
    # _user = app_service.find_user_data(serialize=True)
    # print(f"User: {_user}")
    print(records)
