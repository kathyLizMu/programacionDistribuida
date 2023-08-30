from __future__ import annotations
import json
from pathlib import Path

PASTA_CONTAS = "contas"


class Conta:
    def __init__(self, rg: str, nome: str, saldo: float):
        """
        Construtor da classe Conta.
        :param rg: RG do cliente.
        :type rg: str
        :param nome: Nome do cliente.
        :type nome: str
        :param saldo: Saldo da conta.
        :type saldo: float
        """
        self.rg = rg
        self.nome = nome
        self.saldo = saldo

    @staticmethod
    def obter_conta(rg: str) -> Conta | None:
        """
        Obtém uma conta a partir do RG do cliente.
        :rtype: Conta or None
        """
        arquivo = Path(f"{PASTA_CONTAS}/{rg}.json")
        if arquivo.exists():
            with open(arquivo, "r") as f:
                return Conta(**json.load(f))
        return None

    def salvar(self) -> None:
        """
        Salva a conta no arquivo de banco de dados.
        """
        arquivo = Path(f"{PASTA_CONTAS}/{self.rg}.json")
        with open(arquivo, "w") as f:
            json.dump(self.__dict__, f)

    def depositar(self, valor: float) -> None:
        """
        Deposita um valor na conta.
        :param valor: Valor a ser depositado.
        :type valor: float
        """
        self.saldo += valor
        self.salvar()

    def sacar(self, valor: float) -> None:
        """
        Sacar um valor da conta.
        :param valor: Valor a ser sacado.
        :type valor: float
        """
        self.saldo -= valor
        self.salvar()

    def transferir(self, conta_destino: Conta, valor: float) -> None:
        """
        Transfere um valor de uma conta para outra.
        :param conta_destino: Conta de destino.
        :type conta_destino: Conta
        :param valor: Valor a ser transferido.
        :type valor: float
        """
        self.sacar(valor)
        conta_destino.depositar(valor)
        self.salvar()
        conta_destino.salvar()
