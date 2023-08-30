from __future__ import annotations
from re import match
from abc import abstractmethod

from recursos.enums import Operacoes, Resposta


class Protocolo:
    pattern = '^t:([0-9]+).*$'
    tempo = 0

    @abstractmethod
    def encapsular(self) -> str:
        """
        Encapsula o objeto numa ‘string’.
        """
        pass

    @staticmethod
    @abstractmethod
    def desencapsular(mensagem: str) -> Protocolo:
        """
        Desencapsula a mensagem num objeto.
        :param mensagem: Mensagem a ser desencapsulada.
        :type mensagem: str
        """
        pass

    @staticmethod
    def obter_tempo(mensagem: str) -> int:
        """
        Obtém o tempo da mensagem.
        :param mensagem: Mensagem a ser analisada.
        :type mensagem: str
        :rtype: int
        """
        return int(match(Protocolo.pattern, mensagem).group(1))


class OperacaoSaldo(Protocolo):
    pattern = '^t:([0-9]+)\|op:1\|rg:([0-9]{1,10})$'

    def __init__(self, tempo: int, rg: str):
        self.tempo = tempo
        self.rg = rg

    def encapsular(self) -> str:
        return f"t:{self.tempo}|op:{Operacoes.SALDO.value}|rg:{self.rg}"

    @staticmethod
    def desencapsular(mensagem: str) -> OperacaoSaldo:
        tempo, rg = match(OperacaoSaldo.pattern, mensagem).groups()
        return OperacaoSaldo(tempo=int(tempo), rg=str(rg))


class OperacaoSaque(Protocolo):
    pattern = r'^t:([0-9]+)\|op:2\|rg:([0-9]{1,10})\|valor:(.*)$'

    def __init__(self, tempo: int, rg: str, valor: float):
        self.tempo = tempo
        self.rg = rg
        self.valor = valor

    def encapsular(self) -> str:
        return f"t:{self.tempo}|op:{Operacoes.SAQUE.value}|rg:{self.rg}|valor:{self.valor}"

    @staticmethod
    def desencapsular(mensagem: str) -> OperacaoSaque:
        tempo, rg, valor = match(OperacaoSaque.pattern, mensagem).groups()
        return OperacaoSaque(tempo=int(tempo), rg=str(rg), valor=float(valor))


class OperacaoDeposito(Protocolo):
    pattern = r'^t:([0-9]+)\|op:3\|rg:([0-9]{1,10})\|valor:(.*)$'

    def __init__(self, tempo: int, rg: str, valor: float):
        self.tempo = tempo
        self.rg = rg
        self.valor = valor

    def encapsular(self) -> str:
        return f"t:{self.tempo}|op:{Operacoes.DEPOSITO.value}|rg:{self.rg}|valor:{self.valor}"

    @staticmethod
    def desencapsular(mensagem: str) -> OperacaoDeposito:
        tempo, rg, valor = match(OperacaoDeposito.pattern, mensagem).groups()
        return OperacaoDeposito(tempo=int(tempo), rg=str(rg), valor=float(valor))


class OperacaoTransferencia(Protocolo):
    pattern = r'^t:([0-9]+)\|op:4\|rg_origem:([0-9]{1,10})\|rg_destino:([0-9]{1,10})\|valor:(.*)$'

    def __init__(self, tempo: int, rg_origem: str, rg_destino: str, valor: float):
        self.tempo = tempo
        self.rg_origem = rg_origem
        self.rg_destino = rg_destino
        self.valor = valor

    def encapsular(self) -> str:
        return f"t:{self.tempo}|op:{Operacoes.TRANSFERENCIA.value}|rg_origem:{self.rg_origem}|rg_destino:{self.rg_destino}|valor:{self.valor}"

    @staticmethod
    def desencapsular(mensagem: str) -> OperacaoTransferencia:
        tempo, rg_origem, rg_destino, valor = match(OperacaoTransferencia.pattern, mensagem).groups()
        return OperacaoTransferencia(
            tempo=int(tempo),
            rg_origem=str(rg_origem),
            rg_destino=str(rg_destino),
            valor=float(valor)
        )


class OperacaoLogin(Protocolo):
    pattern = r'^t:([0-9]+)\|op:6\|rg:([0-9]{1,10})$'

    def __init__(self, tempo: int, rg: str):
        self.tempo = tempo
        self.rg = rg

    def encapsular(self) -> str:
        return f"t:{self.tempo}|op:{Operacoes.LOGIN.value}|rg:{self.rg}"

    @staticmethod
    def desencapsular(mensagem: str) -> OperacaoLogin:
        tempo, rg = match(OperacaoLogin.pattern, mensagem).groups()
        return OperacaoLogin(tempo=int(tempo), rg=str(rg))


class RespostaSucesso(Protocolo):
    pattern = r'^t:([0-9]+)\|s:0\|resposta:(.*)$'

    def __init__(self, tempo: int, resposta: str):
        self.tempo = tempo
        self.resposta = resposta

    def encapsular(self) -> str:
        return f"t:{self.tempo}|s:{Resposta.OK.value}|resposta:{self.resposta}"

    @staticmethod
    def desencapsular(mensagem: str) -> RespostaSucesso:
        tempo, resposta = match(RespostaSucesso.pattern, mensagem).groups()
        return RespostaSucesso(tempo=int(tempo), resposta=str(resposta))


class RespostaErro(Protocolo):
    pattern = r'^t:([0-9]+)\|s:1\|resposta:(.*)$'

    def __init__(self, tempo: int, resposta: str):
        self.tempo = tempo
        self.resposta = resposta

    def encapsular(self) -> str:
        return f"t:{self.tempo}|s:{Resposta.ERRO.value}|resposta:{self.resposta}"

    @staticmethod
    def desencapsular(mensagem: str) -> RespostaErro:
        tempo, resposta = match(RespostaErro.pattern, mensagem).groups()
        return RespostaErro(tempo=int(tempo), resposta=str(resposta))
