import re

CONFIGURACAO_PADRAO = (64, 4, 1)


def ler_configuracoes(args):
    if not args:
        return [CONFIGURACAO_PADRAO] * 3

    texto = re.sub(r"\s*:\s*", ":", " ".join(args))
    partes = texto.split()
    if len(partes) not in (2, 3):
        raise ValueError("informe as configurações da iL1 e da dL1, e opcionalmente da L2")

    configuracoes = []
    for parte in partes:
        campos = parte.split(":")
        if len(campos) != 3 or not all(c.isdigit() for c in campos):
            raise ValueError(f"configuração inválida: {parte} (use nsets:bsize:assoc)")
        configuracoes.append(tuple(int(c) for c in campos))
    return configuracoes


def ler_enderecos(caminho):
    with open(caminho, "rb") as arquivo:
        dados = arquivo.read()
    return [int.from_bytes(dados[i : i + 4], "big") for i in range(0, len(dados), 4)]
