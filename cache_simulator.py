import random
import sys

from cache import Cache
from entrada import ler_configuracoes, ler_enderecos

USO = (
    "Uso:\n"
    "  python cache_simulator.py arquivo_de_entrada\n"
    "  python cache_simulator.py <nsets_iL1>:<bsize_iL1>:<assoc_iL1> "
    "<nsets_dL1>:<bsize_dL1>:<assoc_dL1> arquivo_de_entrada\n"
    "  python cache_simulator.py <nsets_iL1>:<bsize_iL1>:<assoc_iL1> "
    "<nsets_dL1>:<bsize_dL1>:<assoc_dL1> <nsets_L2>:<bsize_L2>:<assoc_L2> arquivo_de_entrada"
)

LIMITE_DADOS = 512 * 1024 * 1024


class Simulador:
    def __init__(self, il1, dl1, l2=None):
        self.il1, self.dl1, self.l2 = il1, dl1, l2
        self.acessos = 0

    @property
    def caches(self):
        return [c for c in (self.il1, self.dl1, self.l2) if c is not None]

    def acessar(self, endereco):
        self.acessos += 1
        l1 = self.dl1 if endereco < LIMITE_DADOS else self.il1
        if not l1.acessar(endereco) and self.l2 is not None:
            self.l2.acessar(endereco)

    def relatorio(self):
        partes = [f"Total de acessos: {self.acessos}"]
        partes += [cache.relatorio() for cache in self.caches]
        return "\n\n".join(partes)


def main(args):
    if not args:
        print(USO, file=sys.stderr)
        return 1

    rng = random.Random()
    try:
        configuracoes = ler_configuracoes(args[:-1])
        caches = [
            Cache(nome, *config, rng) for nome, config in zip(("iL1", "dL1", "L2"), configuracoes)
        ]
    except ValueError as erro:
        print(f"Erro: {erro}\n\n{USO}", file=sys.stderr)
        return 1

    try:
        enderecos = ler_enderecos(args[-1])
    except OSError as erro:
        print(f"Erro ao ler o arquivo: {erro}", file=sys.stderr)
        return 1

    simulador = Simulador(*caches)
    for endereco in enderecos:
        simulador.acessar(endereco)

    print(simulador.relatorio())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
