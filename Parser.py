from tokenize import Token
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
        print("/////FIRST/////")
        for key in firstpos.keys():
            print(key+": ", end="")
            print(firstpos[key])
        followpos = gramatica.followpost()
        print("/////FOLLOW/////")
        for key in followpos.keys():
            print(key+": ", end="")
            print(followpos[key])
        for nt in gramatica.nao_terminais:
            if firstpos[nt] & followpos[nt] and nt in gramatica.anulaveis():
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

                # Preenchimento de first
                # print(producao)
                first = gramatica.first_prod(producao)
                # print(first)

                # Preenchimento de quando for follow
                if producao == "&" or "&" in first:
                    for terminal in followpos[nt]:
                        if not self.table[nt][terminal] is None:
                            for e in self.table:
                                print(e, self.table[e])
                            raise RuntimeError(f"Tentei colocar duas producoes na tabela LL1 {nt} {terminal}")
                        # print(f"folow: inseri {producao} em {nt} {terminal}")
                        self.table[nt][terminal] = producao
                    # continue

                for terminal in first:
                    if terminal == "&": continue
                    if not self.table[nt][terminal] is None:
                        for e in self.table:
                                print(e, self.table[e])
                        raise RuntimeError(f"Tentei colocar duas producoes na tabela LL1 {nt} {terminal}")
                    # print(f"first: inseri {producao} em {nt} {terminal}")
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
        # cabecalho += [terminal for terminal in self.table[self.gramatica.inicial]]
        cabecalho += [terminal for terminal in self.table[self.gramatica.inicial] if terminal != "&"]
        with open(filename, "w") as csv:
            csv.write(",".join(cabecalho)+"\n")
            for nt, linha in self.table.items():
                arquivo_linha = [nt]
                # arquivo_linha += [" " for terminal in linha]
                arquivo_linha += [" " for terminal in linha if terminal != "&"]
                for terminal in linha:
                    if terminal == "&":
                        continue
                    producao_str = self.table[nt][terminal]
                    if producao_str != None:
                        arquivo_linha[cabecalho.index(terminal)] = producao_str.replace('"', '"""').replace(',', '","')
                csv.write(",".join(arquivo_linha)+"\n")

class AnalisadorSintatico:
    def __init__(self, folder: str, Lexer:TokenDriver, validar = True) -> None:
        self.gramatica = Gramatica().from_file_preprocess(folder+"/grammar").tratada()
        print("Gramatica Tratada com sucesso!")
        self.token = Lexer.gerador()
        self.tabela = ParsingTable(self.gramatica)
        self.tabela.to_csv(folder+"/tabela_sintatica.csv")
        self.pilha = Pilha()
        if validar: self.validate(Gramatica().from_file_preprocess(folder+"/grammar"))

    # Faz o parsing dos tokens e valida a sintaxe
    def parse(self, show_stack = False, token: TokenDriver = None):

        if token is None:
            token = self.token
        # Inicializacao da pilha
        self.pilha.clear()
        self.pilha.push("$")
        self.pilha.push(self.gramatica.inicial)

        # Leitura do token
        token_analisado = None
        token_analisado = next(token)

        topo = self.pilha.top()

        if show_stack:
            pilha_str = None
            print("-------------------")

        while topo != "$":
            if show_stack:
                pilha_str = self.pilha.list()
                # print(pilha_str)
                pilha_str.reverse()
                pilha_str = " , ".join(pilha_str)
                print(f"tk: {token_analisado:<10} ", end=" ")
            # Token no topo da pilha correto
            if topo == token_analisado:
                if show_stack:
                    print(f"top: {topo:<18} ", end=" ")
                self.pilha.pop()
                try:
                    token_analisado = next(token)
                except StopIteration:
                    return False
            # Token no topo da pilha incorreto
            elif topo in self.gramatica.terminais:
                return False#raise SyntaxError("Erro de Sintaxe no arquivo fonte (Essa msg eh do trabalho)")
            # Producao inexistente
            elif self.tabela[topo][token_analisado] is None:
                return False#raise SyntaxError("Erro de Sintaxe no arquivo fonte (Essa msg eh do trabalho)")
            # Producao na pilha
            else:
                producao = self.tabela[topo][token_analisado]
                if show_stack:
                    print(f"prod: {producao:<18} ", end = "")
                self.pilha.pop()
                simbolos = list(producao)
                simbolos.reverse()
                for simbolo in simbolos:
                    self.pilha.push(simbolo)
            topo = self.pilha.top()
            while topo == "&":
                self.pilha.pop()
                topo = self.pilha.top()
            if show_stack:
                print(f"s: [{pilha_str : >50}]")
        if token_analisado != "$":
            return False
            # raise SyntaxError("Erro de Sintaxe no arquivo fonte (Essa msg eh do trabalho)")
        return True

    # Gera palavras 100 palavras aleatorias a partir da gramatica e faz o parsgin delas
    def validate(self, gramatica_original):
        total = 100
        done = set()
        with open("validation.txt", "w") as _: pass
        with open("validation.txt", "a") as arq_val:
            for _ in range(total * 100):
                if len(done) >= total: return
                sentenca: str = gramatica_original.generate_word(200)
                if not sentenca is None and sentenca not in done:
                    done.add(sentenca)
                    arq_val.write(sentenca + "\n")
                    driver = TokenDriver(sentenca.split())
                    if not self.parse(token=driver.gerador()):
                        raise SyntaxError(f"Parseei errado uma sentenca gerada pela minha propria gramatica: {sentenca}")
        print(f"Validacao de {total} sentencas completo!")

if __name__ == "__main__":
    pasta = "compiladores"
    driver = TokenDriver("None".split())
    parser = AnalisadorSintatico(pasta, driver, True)
    # print(parser.parse(True, TokenDriver("c c c c c $".split()).gerador(),))