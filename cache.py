import random
from collections import OrderedDict


def potencia_de_dois(n):
    return n > 0 and n & (n - 1) == 0


def razao(a, b):
    return a / b if b else 0.0


class Cache:
    def __init__(self, nome, nsets, bsize, assoc, rng=None):
        if not potencia_de_dois(nsets) or not potencia_de_dois(bsize):
            raise ValueError(f"{nome}: nsets e bsize devem ser potências de 2")
        if assoc < 1:
            raise ValueError(f"{nome}: assoc deve ser maior que zero")

        self.nome, self.nsets, self.bsize, self.assoc = nome, nsets, bsize, assoc
        self.bits_offset = bsize.bit_length() - 1
        self.bits_indice = nsets.bit_length() - 1
        if self.bits_offset + self.bits_indice > 32:
            raise ValueError(f"{nome}: nsets * bsize excede o espaço de endereçamento de 32 bits")

        self.tags = [[None] * assoc for _ in range(nsets)]
        self.rng = rng or random.Random()

        self.blocos_vistos = set()
        self.sombra = OrderedDict()

        self.acessos = self.hits = 0
        self.miss_compulsorio = self.miss_capacidade = self.miss_conflito = 0

    @property
    def tamanho(self):
        return self.nsets * self.bsize * self.assoc

    @property
    def misses(self):
        return self.miss_compulsorio + self.miss_capacidade + self.miss_conflito

    def acessar_sombra(self, bloco):
        if bloco in self.sombra:
            self.sombra.move_to_end(bloco)
            return True
        self.sombra[bloco] = None
        if len(self.sombra) > self.nsets * self.assoc:
            self.sombra.popitem(last=False)
        return False

    def acessar(self, endereco):
        self.acessos += 1
        bloco = endereco >> self.bits_offset
        indice = bloco & (self.nsets - 1)
        tag = bloco >> self.bits_indice
        tags = self.tags[indice]

        hit_na_sombra = self.acessar_sombra(bloco)

        if tag in tags:
            self.hits += 1
            return True

        if bloco not in self.blocos_vistos:
            self.blocos_vistos.add(bloco)
            self.miss_compulsorio += 1
        elif not hit_na_sombra:
            self.miss_capacidade += 1
        else:
            self.miss_conflito += 1

        via = tags.index(None) if None in tags else self.rng.randrange(self.assoc)
        tags[via] = tag
        return False

    def relatorio(self):
        misses = self.misses
        linhas = [
            f"Cache {self.nome} ({self.nsets} conjuntos x {self.bsize} bytes x "
            f"{self.assoc} vias = {self.tamanho} bytes)",
            f"{'  Acessos:':<28}{self.acessos}",
            f"{'  Hits:':<28}{self.hits} (hit ratio: {razao(self.hits, self.acessos):.4f})",
            f"{'  Misses:':<28}{misses} (miss ratio: {razao(misses, self.acessos):.4f})",
        ]
        for rotulo, valor in [
            ("    Compulsórios:", self.miss_compulsorio),
            ("    Capacidade + conflito:", self.miss_capacidade + self.miss_conflito),
            ("      Capacidade:", self.miss_capacidade),
            ("      Conflito:", self.miss_conflito),
        ]:
            linhas.append(f"{rotulo:<28}{valor} ({razao(valor, misses):.4f} dos misses)")
        return "\n".join(linhas)
