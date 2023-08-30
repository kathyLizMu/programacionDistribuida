from __future__ import annotations

import signal
import socket
import select
import threading
import os
import sys



from recursos import utils
from recursos.protocolo import *
from recursos.conta import Conta

PORTA_PADRAO = 5000

lock = threading.RLock()


class Servidor:
    def __init__(self) -> None:
        """
        Construtor da classe Servidor.
        """
        if not utils.verificar_porta(porta=PORTA_PADRAO):
            print('El puerto ya está en uso')
            exit()

        self.porta = PORTA_PADRAO
        self.socket = None
        self.relogio = 0
        self.disponivel = False

    def incrementar_relogio(self) -> None:
        """
        Incrementa o relógio do servidor.
        """
        with lock:
            self.relogio += 1
        print(f"Relógio Lógico Atualizado: {self.relogio}")

    def atualizar_tempo(self, tempo: int) -> None:
        """
        Atualiza o relógio com o tempo recebido, se ele for maior que o tempo atual e incrementa o relógio.
        """
        with lock:
            self.relogio = max(self.relogio, tempo) + 1
        print(f'Relógio Lógico Atualizado: {self.relogio}')

    def obter_e_incrementar_tempo(self) -> int:
        """
        Incrementa o relógio do servidor e retorna o valor atualizado.
        :rtype: int
        """
        self.incrementar_relogio()
        return self.relogio

    def iniciar(self) -> None:
        """
        Inicia o servidor.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', self.porta))
        self.socket.listen(1)
        self.disponivel = True
        print(f"El servidor se inició en el puerto {self.porta}")

    def aceitar_conexao(self) -> None:
        """
        Aceita uma conexão de um cliente e processa as mensagens dele, numa nova thread.
        """
        cliente_socket, cliente_socket_host = self.socket.accept()
        print(f"Nuevo cliente conectado {cliente_socket_host}")
        threading.Thread(target=self.processar_operacoes_cliente, args=(cliente_socket,)).start()

    def processar_operacoes_cliente(self, cliente_socket) -> None:
        """
        Processa as operações do cliente.
        :param cliente_socket: Socket do cliente.
        :type cliente_socket: socket.socket
        """
        while self.disponivel:
            try:
                ready_to_read, ready_to_write, in_error = select.select(
                    [cliente_socket, ],
                    [cliente_socket, ],
                    [],
                    5
                )
            except select.error:
                cliente_socket.shutdown(2)
                cliente_socket.close()
                print('error de conexion')
                break
            if len(ready_to_read) > 0:
                mensagem = cliente_socket.recv(utils.TAMANHO_BUFFER_PADRAO).decode()
                if mensagem:
                    self.processar_operacao(cliente_socket=cliente_socket, mensagem=mensagem)
                else:
                    break
            if len(ready_to_write) > 0:
                pass
            if len(in_error) > 0:
                break

        cliente_socket.close()
        print('Cliente desconectado')

    def encerrar(self) -> None:
        """
        Encerra o servidor.
        """
        print('Apagando...')
        self.desconectar()
        exit()

    def desconectar(self) -> None:
        """
        Desconecta o servidor.
        """
        self.disponivel = False
        self.socket.close()

    @staticmethod
    def criar() -> Servidor:
        """
        Cria uma instância do servidor.
        :rtype: Servidor
        """
        servidor = Servidor()
        servidor.iniciar()

        signal.signal(signal.SIGINT, lambda signum, frame: servidor.encerrar())
        return servidor

    def processar_operacao_saldo(self, cliente_socket, mensagem: str) -> None:
        """
        Processa a operação de saldo.
        :param cliente_socket: Socket do cliente.
        :type cliente_socket: socket.socket
        :param mensagem: Comando recebido do cliente.
        :type mensagem: str
        """
        solicitacao = OperacaoSaldo.desencapsular(mensagem=mensagem)
        rg = str(solicitacao.rg)

        with lock:
            conta = Conta.obter_conta(rg=rg)
            if conta:
                resposta = RespostaSucesso(tempo=self.obter_e_incrementar_tempo(), resposta=f"Saldo: {conta.saldo}")
            else:
                resposta = RespostaErro(tempo=self.obter_e_incrementar_tempo(), resposta='Cliente não encontrado')
            cliente_socket.send(resposta.encapsular().encode())

    def processar_operacao_saque(self, cliente_socket, mensagem: str) -> None:
        """
        Processa a operação de saque.
        :param cliente_socket: Socket do cliente.
        :type cliente_socket: socket.socket
        :param mensagem: Comando recebido do cliente.
        :type mensagem: str
        """
        solicitacao = OperacaoSaque.desencapsular(mensagem=mensagem)
        rg = str(solicitacao.rg)

        with lock:
            conta = Conta.obter_conta(rg=rg)
            if conta:
                if conta.saldo >= solicitacao.valor:
                    conta.sacar(valor=solicitacao.valor)
                    resposta = RespostaSucesso(tempo=self.obter_e_incrementar_tempo(), resposta='Saque realizado com sucesso')
                else:
                    resposta = RespostaErro(tempo=self.obter_e_incrementar_tempo(), resposta='Saldo insuficiente')
            else:
                resposta = RespostaErro(tempo=self.obter_e_incrementar_tempo(), resposta='Cliente não encontrado')
            cliente_socket.send(resposta.encapsular().encode())

    def processar_operacao_deposito(self, cliente_socket, mensagem: str) -> None:
        """
        Processa a operação de depósito.
        :param cliente_socket: Socket do cliente.
        :type cliente_socket: socket.socket
        :param mensagem: Comando recebido do cliente.
        :type mensagem: str
        """
        solicitacao = OperacaoDeposito.desencapsular(mensagem=mensagem)
        with lock:
            rg = str(solicitacao.rg)

            conta = Conta.obter_conta(rg=rg)
            if conta:
                conta.depositar(valor=solicitacao.valor)
                resposta = RespostaSucesso(tempo=self.obter_e_incrementar_tempo(), resposta='Depósito realizado com sucesso')
            else:
                resposta = RespostaErro(tempo=self.obter_e_incrementar_tempo(), resposta='Cliente não encontrado')

            cliente_socket.send(resposta.encapsular().encode())

    def processar_operacao_transferencia(self, cliente_socket, mensagem: str) -> None:
        """
        Processa a operação de transferência.
        :param cliente_socket: Socket do cliente.
        :type cliente_socket: socket.socket
        :param mensagem: Comando recebido do cliente.
        :type mensagem: str
        """
        solicitacao = OperacaoTransferencia.desencapsular(mensagem=mensagem)

        if solicitacao.rg_origem == solicitacao.rg_destino:
            resposta = RespostaErro(tempo=self.obter_e_incrementar_tempo(), resposta='Não é possível transferir para a mesma conta')
            cliente_socket.send(resposta.encapsular().encode())
            return

        with lock:
            conta_origem = Conta.obter_conta(rg=solicitacao.rg_origem)
            conta_destino = Conta.obter_conta(rg=solicitacao.rg_destino)

            if conta_origem is None:
                resposta = RespostaErro(tempo=self.obter_e_incrementar_tempo(), resposta='Conta de origem não encontrada')
                cliente_socket.send(resposta.encapsular().encode())
                return
            if conta_destino is None:
                resposta = RespostaErro(tempo=self.obter_e_incrementar_tempo(), resposta='Conta de destino não encontrada')
                cliente_socket.send(resposta.encapsular().encode())
                return
            if conta_origem.saldo < solicitacao.valor:
                resposta = RespostaErro(tempo=self.obter_e_incrementar_tempo(), resposta='Saldo insuficiente')
                cliente_socket.send(resposta.encapsular().encode())
                return

            conta_origem.transferir(conta_destino=conta_destino, valor=solicitacao.valor)
            resposta = RespostaSucesso(tempo=self.obter_e_incrementar_tempo(), resposta='Transferência realizada com sucesso')
            cliente_socket.send(resposta.encapsular().encode())
            return

    def processar_operacao_login(self, cliente_socket, mensagem: str) -> None:
        """
        Processa a operação de ‘login’.
        :param cliente_socket: Socket do cliente.
        :type cliente_socket: socket.socket
        :param mensagem: Comando recebido do cliente.
        :type mensagem: str
        """
        solicitacao = OperacaoLogin.desencapsular(mensagem=mensagem)
        rg = str(solicitacao.rg)
        conta = Conta.obter_conta(rg=rg)
        if conta:
            resposta = RespostaSucesso(tempo=self.obter_e_incrementar_tempo(), resposta='Login realizado con exito')
        else:
            resposta = RespostaErro(tempo=self.obter_e_incrementar_tempo(), resposta='Cliente no encontrado')
        cliente_socket.send(resposta.encapsular().encode())

    def processar_operacao(self, cliente_socket, mensagem: str) -> None:
        """
        Atualiza o relógio lógico do servidor e processa a mensagem do cliente.
        :param cliente_socket: Socket do cliente.
        :type cliente_socket: socket.socket
        :param mensagem: Comando recebido do cliente.
        :type mensagem: str
        :rtype: None
        """
        self.atualizar_tempo(tempo=Protocolo.obter_tempo(mensagem))

        if match(pattern=OperacaoSaldo.pattern, string=mensagem):
            self.processar_operacao_saldo(cliente_socket, mensagem)
        elif match(pattern=OperacaoSaque.pattern, string=mensagem):
            self.processar_operacao_saque(cliente_socket, mensagem)
        elif match(pattern=OperacaoDeposito.pattern, string=mensagem):
            self.processar_operacao_deposito(cliente_socket, mensagem)
        elif match(pattern=OperacaoTransferencia.pattern, string=mensagem):
            self.processar_operacao_transferencia(cliente_socket, mensagem)
        elif match(pattern=OperacaoLogin.pattern, string=mensagem):
            self.processar_operacao_login(cliente_socket, mensagem)
        else:
            resposta = RespostaErro(tempo=self.obter_e_incrementar_tempo(), resposta='Operaçao inválida')
            cliente_socket.send(resposta.encapsular().encode())


def main():
    """
    Função principal.
    """
    servidor = Servidor.criar()
    print('Esperando conexión...')
    while servidor.disponivel:
        servidor.aceitar_conexao()


if __name__ == '__main__':
    main()
    exit()
