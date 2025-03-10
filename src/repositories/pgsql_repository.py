from sqlalchemy.orm import joinedload

from src.models import Redlie


class PgsqlRepository():
    def __init__(self):
        self.user_model = Redlie.User
        self.muestra_model = Redlie.Muestra
        self.participante_model = Redlie.Participante
        self.vocablo_model = Redlie.Vocablo
        self.indice_disponibilidad_model = Redlie.IndiceDisponibilidad
        self._session = None

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        self._session = value

    def find_user(self, username):
        query = self.session.query(self.user_model)
        # query.options(joinedload(Redlie.User.muestras))
        return query.filter_by(username=username).first()

    def find_user_muesta(self, muestra_id):
        query = self.session.query(self.muestra_model)
        query.options(joinedload(Redlie.Muestra.participantes), joinedload(Redlie.Muestra.indices_disponibilidad))
        return query.filter_by(id=muestra_id).first()

    def get_muesta(self, muestra_id):
        query = self.session.query(self.muestra_model)
        return query.filter_by(id=muestra_id).first()
