from enum import Enum


class Operacoes(Enum):
    SALDO = 1
    SAQUE = 2
    DEPOSITO = 3
    TRANSFERENCIA = 4
    SINCRONIZAR_RELOGIO = 5
    LOGIN = 6
    SAIR = 0


class Resposta(Enum):
    OK = 0
    ERRO = 1
