from enum import Enum

class StatusEnum(str, Enum):
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"
    REALIZADA = "REALIZADA"

class SituacaoCurso(str, Enum):
    ABERTO = "ABERTO"
    CANCELADO = "CANCELADO"
    REALIZADO = "REALIZADO"