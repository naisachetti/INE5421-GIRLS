from Gramatica import Gramatica
from Pilha import Pilha

class TokenDriver:
    def __init__(self, tokens_validos: list) -> None:
        self.tokens = tokens_validos

    def gerador(self):
        for element in self.tokens:
            yield element

class ParsingTable:
    def __init__(self, gramatica: Gramatica) -> None:
        self.gramatica = gramatica
        terminais = gramatica.terminais.copy()
        terminais += "$"
        firstpos = gramatica.firspost()
        followpos = gramatica.followpost()
        # print(firstpos, followpos)
        for nt in gramatica.nao_terminais:
            if firstpos[nt].intersection(followpos[nt]) and nt in gramatica.anulaveis():
                print(gramatica)
                raise SyntaxError(f"Gramatica nao eh LL1 nt: {nt} first:{firstpos[nt]}, follow:{followpos[nt]}")
        self.table = {}

        # Criacao da tabela
        for nt in gramatica.nao_terminais:
            linha = {terminal: None for terminal in terminais}
            self.table[nt] = linha

        # Preenchimento da tabela
        for nt, producoes in gramatica.producoes.items():
            for producao in producoes:

                # Preenchimento de quando for follow
                if producao == "&":
                    for terminal in followpos[nt]:
                        if not self.table[nt][terminal] is None:
                            raise RuntimeError(f"Tentei colocar duas producoes na tabela LL1 {nt} {terminal}")
                        self.table[nt][terminal] = producao
                    continue

                # Preenchimento de first
                # print("prod",producao)
                first = gramatica.first_prod(producao)
                if "&" in first:
                    raise RuntimeError
                # print(nt, first)
                for terminal in first:
                    if not self.table[nt][terminal] is None:
                        raise RuntimeError(f"Tentei colocar duas producoes na tabela ll1 {nt} {terminal}")
                    self.table[nt][terminal] = producao

    def __repr__(self):
        saida = ""
        for label, linha in self.table.items():
            saida += f"{label}: {linha}\n"
        return saida

    def __getitem__(self, chave):
        return self.table[chave]

    def to_csv(self, filename: str):
        cabecalho: list = ["NT"]
        cabecalho += [terminal for terminal in self.table[self.gramatica.inicial] if terminal != "&"]
        with open(filename, "w") as csv:
            csv.write(",".join(cabecalho)+"\n")
            for nt, linha in self.table.items():
                arquivo_linha = [nt]
                arquivo_linha += [" " for terminal in linha if terminal != "&"]
                for terminal in linha:
                    if terminal == "&":
                        continue
                    producao_str = self.table[nt][terminal]
                    if producao_str != None:
                        arquivo_linha[cabecalho.index(terminal)] = producao_str
                csv.write(",".join(arquivo_linha)+"\n")

class AnalisadorSintatico:
    def __init__(self, folder: str, Lexer:TokenDriver) -> None:
        self.gramatica = Gramatica().from_file(folder+"/grammar").tratada()
        self.token = Lexer.gerador()
        self.tabela = ParsingTable(self.gramatica)
        self.pilha = Pilha()
        self.validate(self.gramatica)

    # Faz o parsing dos tokens e valida a sintaxe
    def parse(self, show_stack = False):
        
        # Inicializacao da pilha
        self.pilha.clear()
        self.pilha.push("$")
        self.pilha.push(self.gramatica.inicial)

        # Leitura do token
        token_analisado = None
        token_analisado = next(self.token)

        topo = self.pilha.top()

        if show_stack: print("-------------------")

        while topo != "$":
            if show_stack: print(topo, token_analisado, self.pilha, end=" ")
            # Token no topo da pilha correto
            if topo == token_analisado:
                if show_stack: print(topo)
                self.pilha.pop()
                token_analisado = next(self.token)
            # Token no topo da pilha incorreto
            elif topo in self.gramatica.terminais:
                raise SyntaxError("Erro de Sintaxe no arquivo fonte (Essa msg eh do trabalho)")
            # Producao inexistente
            elif self.tabela[topo][token_analisado] is None:
                raise SyntaxError("Erro de Sintaxe no arquivo fonte (Essa msg eh do trabalho)")
            # Producao na pilha
            else:
                producao = self.tabela[topo][token_analisado]
                if show_stack: print(producao)
                self.pilha.pop()
                simbolos = list(producao)
                simbolos.reverse()
                for simbolo in simbolos:
                    self.pilha.push(simbolo)
            topo = self.pilha.top()
            while topo == "&":
                self.pilha.pop()
                topo = self.pilha.top()
        if token_analisado != "$":
            raise SyntaxError("Erro de Sintaxe no arquivo fonte (Essa msg eh do trabalho)")
        return True

    # Gera palavras 100 palavras aleatorias a partir da gramatica e faz o parsgin delas
    def validate(self, gramatica):
        total = 100
        validas = 0
        for _ in range(10000):
            sentenca = gramatica.generate_word(100)
            if not sentenca is None:
                driver = TokenDriver(sentenca.split())
                try:
                    self.parse(driver)
                except SyntaxError:
                    raise RuntimeError(f"Parseei errado uma sentenca gerada pela minha propria gramatica: {sentenca}")
                validas += 1
            if validas == total:
                break

if __name__ == "__main__":
    arquivo = "gramatica_ex4.txt"
    pura = Gramatica().from_file(arquivo)
    tratada = Gramatica().from_file(arquivo).tratada()
    # p = ParsingTable(tratada)
    # parser = AnalisadorSintatico("defauld", TokenDriver(""))
    # parser.validate(pura)
