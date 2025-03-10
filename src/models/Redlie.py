from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime, server_default=func.now())
    last_login_at = Column(DateTime, server_default=func.now())

    muestras = relationship("Muestra", back_populates="user", cascade="all, delete-orphan")  # , lazy="select")

    @staticmethod
    def create(username, email):
        return User(
            id=username,
            username=username,
            email=email,
            created_at=func.now(),
            last_login_at=func.now()
        )

    def _to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at,
            "last_login_at": self.last_login_at,
            "muestras": [muestra._to_dict() for muestra in self.muestras]
        }

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at,
            "last_login_at": self.last_login_at,
            "muestras": [muestra.to_dict() for muestra in self.muestras]
        }


class Muestra(Base):
    __tablename__ = 'muestras'

    id = Column(String(255), primary_key=True)
    user_id = Column(String(255), ForeignKey('users.id', ondelete='CASCADE'))
    file_name = Column(String(255), nullable=False)
    uploaded_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="muestras")
    participantes = relationship("Participante", back_populates="muestra",
                                 cascade="all, delete-orphan")  # , lazy="select")
    indices_disponibilidad = relationship("IndiceDisponibilidad", back_populates="muestra",
                                          cascade="all, delete-orphan")  # , lazy="select")

    participants_no = Column(Integer, nullable=False, server_default="0")
    indices_no = Column(Integer, nullable=False, server_default="0")
    ni_no = Column(Integer, nullable=False, server_default="0")
    ci_no = Column(Integer, nullable=False, server_default="0")

    @staticmethod
    def create(user_id, file_name):
        # today = datetime.now().strftime("%d-%m-%Y")
        date_time = datetime.now().strftime("%Y-%m-%d-%H-%M")
        id = f"{user_id}-{date_time}"
        return Muestra(id=id, user_id=user_id, file_name=file_name, uploaded_at=func.now(), participants_no=0,
                       indices_no=0, ni_no=0, ci_no=0)

    def update(self, data):
        self.participants_no = data.get("participants_no", self.participants_no)
        self.indices_no = data.get("indices_no", self.indices_no)
        self.ni_no = data.get("ni_no", self.ni_no)
        self.ci_no = data.get("ci_no", self.ci_no)
        # self.last_updated_at = func.now()

    def _to_dict(self):
        return {
            "id": self.id,
            "file_name": self.file_name,
            "uploaded_at": self.uploaded_at,
            "participantes": [],
            # [participante.to_dict() for participante in self.participantes] if self.participantes else [],
            "indices_disponibilidad": [],
            # [indice.to_dict() for indice in self.indices_disponibilidad] if self.indices_disponibilidad else []
            "participants_no": self.participants_no,
            "indices_no": self.indices_no,
            "ni_no": self.ni_no,
            "ci_no": self.ci_no
        }

    def to_dict(self):
        return {
            "id": self.id,
            "file_name": self.file_name,
            "uploaded_at": self.uploaded_at,
            "participantes": [participante.to_dict() for participante in
                              self.participantes] if self.participantes else [],
            "indices_disponibilidad": [indice.to_dict() for indice in
                                       self.indices_disponibilidad] if self.indices_disponibilidad else [],
            "participants_no": self.participants_no,
            "indices_no": self.indices_no,
            "ni_no": self.ni_no,
            "ci_no": self.ci_no
        }


class Participante(Base):
    __tablename__ = 'participantes'

    id = Column(String(255), primary_key=True)
    muestra_id = Column(String(255), ForeignKey('muestras.id', ondelete='CASCADE'))
    ni = Column(Integer, nullable=False)
    ci = Column(Integer, nullable=False)
    edad = Column(Integer, nullable=False)
    sexo = Column(Integer, nullable=False)
    posicion = Column(Integer, nullable=False)

    muestra = relationship("Muestra", back_populates="participantes")
    vocablos = relationship("Vocablo", back_populates="participante", cascade="all, delete-orphan", lazy="select")

    @staticmethod
    def create(id, muestra_id, ni, ci, edad, sexo, posicion):
        return Participante(
            id=id, muestra_id=muestra_id, ni=ni, ci=ci, edad=edad, sexo=sexo, posicion=posicion)

    def to_dict(self):
        return {
            "ni": self.ni,
            "ci": self.ci,
            "edad": self.edad,
            "sexo": self.sexo,
            "posicion": self.posicion,
            "vocablos": [vocablo.vocablo for vocablo in self.vocablos]
        }


class Vocablo(Base):
    __tablename__ = 'vocablos'

    id = Column(String(255), primary_key=True)
    participante_id = Column(String(255), ForeignKey('participantes.id', ondelete='CASCADE'))
    vocablo = Column(String(255), nullable=False)
    posicion = Column(Integer, nullable=False)

    participante = relationship("Participante", back_populates="vocablos")

    @staticmethod
    def create(id, participante_id, vocablo, posicion):
        return Vocablo(
            id=id, participante_id=participante_id, vocablo=vocablo, posicion=posicion)

    def to_dict(self):
        return {
            "vocablo": self.vocablo,
            "posicion": self.posicion
        }


class IndiceDisponibilidad(Base):
    __tablename__ = 'indice_disponibilidad'

    id = Column(String(255), primary_key=True)
    muestra_id = Column(String(255), ForeignKey('muestras.id', ondelete='CASCADE'))
    ci = Column(Integer, nullable=False)
    sexo = Column(String(55), nullable=False)
    vocablo = Column(String(255), nullable=False)
    indice = Column(String(255), nullable=False)

    muestra = relationship("Muestra", back_populates="indices_disponibilidad")

    @staticmethod
    def create(id, muestra_id, ci, sexo, vocablo, indice):
        return IndiceDisponibilidad(
            id=id, muestra_id=muestra_id, ci=ci,
            sexo=sexo, vocablo=vocablo, indice=indice)

    def to_dict(self):
        return {
            "ci": self.ci,
            "sexo": self.sexo,
            "vocablo": self.vocablo,
            "indice": self.indice
        }
