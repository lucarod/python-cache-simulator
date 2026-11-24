# Simulador de Caches (Python)

Simulador funcional e parametrizável de uma hierarquia de caches com até dois níveis:

- **L1 separada (split):** uma cache de instruções (**iL1**) e uma de dados (**dL1**);
- **L2 unificada (opcional):** recebe os misses das duas caches L1.

A cache é endereçada a bytes e os endereços têm 32 bits. O arquivo de entrada contém apenas
leituras. Os primeiros 512 MB da memória (endereços abaixo de `0x20000000`) são a área de
**dados** e vão para a dL1. O restante é a área de **instruções** e vai para a iL1.

A política de substituição é sempre **randômica**. Ela só tem efeito nas caches associativa
por conjunto e totalmente associativa, porque no mapeamento direto cada conjunto tem uma
única via.

## Pré-requisitos

- Python 3.8 ou superior.
- Nenhuma dependência externa.

## Arquivos

| Arquivo              | Conteúdo |
|----------------------|----------|
| `cache_simulator.py` | Programa principal: hierarquia L1/L2 (`Simulador`), linha de comando e relatório. |
| `cache.py`           | Classe `Cache`: acesso, substituição randômica, classificação dos misses e estatísticas de uma cache. |
| `entrada.py`         | Leitura das configurações passadas na linha de comando e do arquivo de endereços. |

Os três arquivos precisam ficar na mesma pasta.

## Como executar

Configuração default, com iL1, dL1 e L2 em mapeamento direto, 64 conjuntos e bloco de 4 bytes:

```powershell
python cache_simulator.py arquivo_de_entrada
```

Somente L1:

```powershell
python cache_simulator.py <nsets_iL1>:<bsize_iL1>:<assoc_iL1> <nsets_dL1>:<bsize_dL1>:<assoc_dL1> arquivo_de_entrada
```

L1 e L2:

```powershell
python cache_simulator.py <nsets_iL1>:<bsize_iL1>:<assoc_iL1> <nsets_dL1>:<bsize_dL1>:<assoc_dL1> <nsets_L2>:<bsize_L2>:<assoc_L2> arquivo_de_entrada
```

Exemplo:

```powershell
python cache_simulator.py 64:4:1 64:4:1 1024:16:4 bin_100.bin
```

Também são aceitos espaços depois dos dois-pontos, por exemplo `64: 4: 1`. O arquivo de
entrada pode ter qualquer nome e extensão.

### Parâmetros

| Campo     | Descrição |
|-----------|-----------|
| `nsets`   | Número de conjuntos (potência de 2). Com `nsets = 1`, a cache é totalmente associativa. |
| `bsize`   | Tamanho do bloco em bytes (potência de 2). |
| `assoc`   | Associatividade (vias por conjunto). Com `assoc = 1`, é mapeamento direto. |

O tamanho de cada cache é `nsets × bsize × assoc` bytes.

O arquivo de entrada é binário: cada endereço ocupa 4 bytes, em ordem big-endian. Se o
tamanho do arquivo não for múltiplo de 4, os bytes que sobram no final são lidos como um
último endereço.

Executar sem argumentos, informar uma configuração inválida (por exemplo, `nsets` ou `bsize`
que não seja potência de 2, ou `assoc` igual a zero) ou um arquivo inexistente gera uma
mensagem de erro e código de saída `1`.

## Saída

Um relatório com o total de acessos e, para cada cache, o número de acessos, de hits (com o
hit ratio) e de misses (com o miss ratio). Os misses aparecem classificados em compulsórios
e capacidade + conflito, e esta última também aparece separada em capacidade e conflito.

```
Total de acessos: 100000

Cache iL1 (64 conjuntos x 4 bytes x 1 vias = 256 bytes)
  Acessos:                  60081
  Hits:                     170 (hit ratio: 0.0028)
  Misses:                   59911 (miss ratio: 0.9972)
    Compulsórios:           15885 (0.2651 dos misses)
    Capacidade + conflito:  44026 (0.7349 dos misses)
      Capacidade:           43958 (0.7337 dos misses)
      Conflito:             68 (0.0011 dos misses)

Cache dL1 (...)

Cache L2 (...)
```

Como a substituição é randômica, os números podem variar um pouco entre execuções quando
alguma cache tem associatividade maior que 1. Isso também afeta uma L2 em mapeamento direto
se a L1 for associativa, porque os acessos que chegam à L2 dependem dos misses da L1. Com
todas as caches em mapeamento direto, como na configuração default, o resultado é sempre o
mesmo.

## Funcionamento

Para cada endereço lido:

1. O endereço vai para a **dL1** se for menor que `0x20000000`, ou para a **iL1** caso contrário.
2. Na cache, o endereço é dividido em **offset** (`log2(bsize)` bits), **índice**
   (`log2(nsets)` bits) e **tag** (bits restantes). Se a tag estiver no conjunto, é um **hit**.
3. Em caso de **miss** na L1, o mesmo endereço é acessado na **L2**, se ela existir.
4. No miss, o bloco vai para uma via vazia do conjunto. Se o conjunto estiver cheio, uma
   via é sorteada para ser substituída.

### Classificação dos misses

Os misses seguem a definição de M. D. Hill e A. J. Smith, *"Evaluating associativity in CPU
caches"* (IEEE Transactions on Computers, 1989):

- **Compulsório:** o primeiro acesso a um bloco. O miss aconteceria mesmo com uma cache infinita.
- **Capacidade:** não é o primeiro acesso, e o miss também aconteceria numa cache totalmente
  associativa de mesmo tamanho com substituição LRU.
- **Conflito:** os demais misses, ou seja, os que essa cache totalmente associativa LRU
  teria evitado.

Para fazer essa separação, cada cache simula em paralelo uma cache "sombra" totalmente
associativa com LRU e o mesmo número de blocos, e guarda o conjunto de blocos já acessados.
A sombra serve só para classificar os misses e não altera o comportamento da cache simulada.

Numa cache totalmente associativa com substituição randômica podem aparecer misses de
conflito: são os misses que a LRU teria evitado e a substituição randômica não evitou.
