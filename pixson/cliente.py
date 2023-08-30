from __future__ import annotations

import sys
import socket
import signal

from recursos import utils
from recursos.protocolo import *

HOST_SERVIDOR = '192.168.0.7'
PORTA_SERVIDOR = 5000


class Cliente:
    def __init__(self, rg: str) -> None:
        """
        Construtor da classe Cliente.
        :param rg: string com o RG do cliente.
        :type rg: str
        """
        self.rg = rg
        self.socket = None
        self.conectado = False
        self.relogio = 0

    def incrementar_relogio(self) -> None:
        """
        Incrementa o relógio.
        """
        self.relogio += 1
        print(f'Reloj Lógico Actualizado: {self.relogio}')

    def atualizar_tempo(self, tempo: int) -> None:
        """
        Atualiza o relógio com o tempo recebido, se ele for maior que o tempo atual e incrementa o relógio.
        """
        self.relogio = max(self.relogio, tempo) + 1
        print(f'Reloj Lógico Actualizado: {self.relogio}')

    def obter_e_incrementar_tempo(self) -> int:
        """
        Incrementa o relógio e retorna o tempo atual.
        """
        self.incrementar_relogio()
        return self.relogio

    def conectar(self) -> None:
        """
        Conecta o cliente ao servidor.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((HOST_SERVIDOR, PORTA_SERVIDOR))
            self.conectado = True
            print(f"Conectado al servidor")
        except ConnectionRefusedError:
            print('Error al conectar al servidor')
            self.encerrar()

    def desconectar(self) -> None:
        """
        Desconecta o cliente do servidor.
        """
        self.socket.close()
        self.conectado = False

    def encerrar(self) -> None:
        """
        Encerra o cliente.
        """
        print('Apagando...')
        self.desconectar()
        exit()

    def enviar_mensagem(self, mensagem: str) -> None:
        """
        Envia uma mensagem para o servidor.
        :param mensagem: Mensagem a ser enviada.
        :type mensagem: str
        """
        if isinstance(mensagem, str):
            mensagem = mensagem.encode()
        self.socket.send(mensagem)

    def receber_mensagem(self) -> str:
        """
        Recebe uma mensagem do servidor e atualiza o relógio lógico.
        :rtype: str
        """
        mensagem = self.socket.recv(utils.TAMANHO_BUFFER_PADRAO).decode()
        self.atualizar_tempo(tempo=Protocolo.obter_tempo(mensagem))
        return mensagem

    def enviar_mensagem_e_imprimir_resposta(self, mensagem: str) -> None:
        """
        Envia uma mensagem para o servidor e imprime a resposta.
        :param mensagem:
        :type mensagem:
        """
        self.enviar_mensagem(mensagem)
        resposta = self.receber_mensagem()
        if match(RespostaSucesso.pattern, resposta):
            resposta = RespostaSucesso.desencapsular(resposta)
        elif match(RespostaErro.pattern, resposta):
            resposta = RespostaErro.desencapsular(resposta)
        print(resposta.resposta)

    @staticmethod
    def criar() -> Cliente | None:
        """
        Cria um cliente.
        :rtype: Cliente or None
        """
        rg = sys.argv[1] if len(sys.argv) > 1 else str(input('Ingrese el ID asociado a la cuenta: '))

        cliente = Cliente(rg)
        cliente.conectar()
        signal.signal(signal.SIGINT, lambda signum, frame: cliente.encerrar())

        cliente.enviar_mensagem(OperacaoLogin(tempo=cliente.obter_e_incrementar_tempo(), rg=rg).encapsular())
        resposta = cliente.receber_mensagem()
        if match(RespostaErro.pattern, resposta):
            resposta = RespostaErro.desencapsular(resposta)
            print(resposta.resposta)
            cliente.encerrar()
            return None
        elif match(RespostaSucesso.pattern, resposta):
            resposta = RespostaSucesso.desencapsular(resposta)
            print(resposta.resposta)
            return cliente

    def processar_comando_saldo(self) -> None:
        """
        Processa o comando de consulta de saldo.
        """
        mensagem = OperacaoSaldo(self.obter_e_incrementar_tempo(), self.rg)
        self.enviar_mensagem_e_imprimir_resposta(mensagem=mensagem.encapsular())

    def processar_comando_saque(self) -> None:
        """
        Processa o comando de saque.
        """
        valor = float(input('Ingrese el monto del retiro: '))
        mensagem = OperacaoSaque(self.obter_e_incrementar_tempo(), self.rg, valor)
        self.enviar_mensagem_e_imprimir_resposta(mensagem=mensagem.encapsular())

    def processar_comando_deposito(self) -> None:
        """
        Processa o comando de depósito.
        """
        valor = float(input('Ingrese el monto del depósito: '))
        mensagem = OperacaoDeposito(self.obter_e_incrementar_tempo(), self.rg, valor)
        self.enviar_mensagem_e_imprimir_resposta(mensagem=mensagem.encapsular())

    def processar_comando_transferencia(self) -> None:
        """
        Processa o comando de transferencia.
        """
        rg_destino = str(input('Ingrese el ID del destinatario: '))
        valor = float(input('Ingrese el monto de la transferencia: '))
        mensagem = OperacaoTransferencia(self.obter_e_incrementar_tempo(), self.rg, rg_destino, valor)
        self.enviar_mensagem_e_imprimir_resposta(mensagem=mensagem.encapsular())


def main() -> None:
    """
    Função principal que inicia o cliente e processa os comandos.
    """
    cliente = Cliente.criar()

    if cliente is not None:
        while cliente.conectado:
            print('\n1 - CONSULTA DE SALDO\n2 - RETIRO\n3 - DEPÓSITO\n4 - TRANSFERENCIA\n0 - SALIR\n')
            comando = input('Ingrese el comando:')
            if isinstance(comando, str) and comando.isdigit():
                comando = int(comando)

            if comando == Operacoes.SALDO.value:
                cliente.processar_comando_saldo()
            elif comando == Operacoes.SAQUE.value:
                cliente.processar_comando_saque()
            elif comando == Operacoes.DEPOSITO.value:
                cliente.processar_comando_deposito()
            elif comando == Operacoes.TRANSFERENCIA.value:
                cliente.processar_comando_transferencia()
            elif comando == Operacoes.SAIR.value:
                break
            else:
                print('Comando inválido!')

        cliente.desconectar()


if __name__ == '__main__':
    main()
    exit()
