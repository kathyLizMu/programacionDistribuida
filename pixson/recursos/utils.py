import socket

TAMANHO_BUFFER_PADRAO = 1024


def verificar_porta(porta: int) -> bool:
    """
    Verifica se a porta está em uso.
    :param porta: Porta a ser verificada.
    :type porta: int
    :rtype: bool
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('', porta))
        s.close()
        return True
    except socket.error:
        s.close()
        return False
