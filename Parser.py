from tokenize import Token
from Gramatica import Gramatica
from Pilha import Pilha

class TokenDriver:
    def __init__(self, tokens_validos: list) -> None:
        self.tokens = tokens_validos

    def gerador(self):
        for element in self.tokens:
            yield (element, element)

class ParsingTable:
    def __init__(self, gramatica: Gramatica, precompiled=False) -> None:
        if precompiled:
            return
        self.gramatica = gramatica
        terminais = gramatica.terminais.copy()
        terminais += "$"
        print("Calculando o firstpos da gramatica...")
        firstpos = gramatica.firspost()
        # print("/////FIRST/////")
        # for key in firstpos.keys():
        #     print(key+": ", end="")
        #     print(firstpos[key])
        print("Calculando o followpos da gramatica... (Isso pode levar um tempo)")
        followpos = gramatica.followpost()
        # print("/////FOLLOW/////")
        # for key in followpos.keys():
        #     print(key+": ", end="")
        #     print(followpos[key])
        for nt in gramatica.nao_terminais:
            if firstpos[nt] & followpos[nt] and nt in gramatica.anulaveis():
                print(gramatica)
                raise SyntaxError(f"Gramatica nao eh LL1 nt: {nt} interseccao:{firstpos[nt]&followpos[nt]} first:{firstpos[nt]}, follow:{followpos[nt]}")
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
        cabecalho += ['"'+terminal+'"' for terminal in self.table[self.gramatica.inicial] if terminal != "&"]
        with open(filename, "w") as csv:
            csv.write("@".join(cabecalho)+"\n")
            for nt, linha in self.table.items():
                arquivo_linha = [nt]
                # arquivo_linha += [" " for terminal in linha]
                arquivo_linha += ["Ø" for terminal in linha if terminal != "&"]
                for terminal in linha:
                    if terminal == "&":
                        continue
                    producao_str = self.table[nt][terminal]
                    if producao_str != None:
                        arquivo_linha[cabecalho.index('"'+terminal+'"')] = producao_str.replace('"', '"""').replace(',', '","')
                csv.write("@".join(arquivo_linha)+"\n")
    
    def from_csv(self, filename: str):
        # Leitura da tabela crua
        raw_table = []
        with open(filename, "r") as arquivo:
            for linha in arquivo:
                raw_table.append(list(map(lambda e: None if e == '"Ø"' else e, linha.split("@"))))
        
        self.table = {}

        print(raw_table[0])
        for i, linha in enumerate(raw_table):
            if not i: continue
            nt = linha[0]
            self.table[nt] = {}
            for terminal, (j, producao) in zip(raw_table[0],enumerate(linha)):
                # Nao terminal da linha
                if not j:
                    continue
                if producao:
                    print(producao)
                    self.table[nt][terminal[1:-1]] = producao[1:-1]
                    continue
                self.table[nt][terminal[1:-1]] = None

        
        return self


class AnalisadorSintatico:
    def __init__(self, folder: str, Lexer:TokenDriver, validar = True, precompiled = False) -> None:
        if precompiled:
            self.gramatica = Gramatica().from_file(folder+"/grammar")
        else:
            self.gramatica = Gramatica().from_file_preprocess(folder+"/grammar").tratada()
        print("Gramatica Tratada com sucesso!")
        self.token = Lexer.gerador()
        if False: #Precompiled
            self.tabela = ParsingTable(self.gramatica, True).from_csv(folder+"/tabela_sintatica.csv")
        else:
            self.tabela = ParsingTable(self.gramatica)
            self.tabela.to_csv(folder+"/tabela_sintatica.csv")
        self.pilha = Pilha()
        self.folder = folder
        if validar: 
            self.validate(Gramatica().from_file_preprocess(folder+"/grammar"))

    # Faz o parsing dos tokens e valida a sintaxe
    def parse(self, show_stack = False, token: TokenDriver = None):
        lista_derivacoes = []

        tokens_lidos = ""
        identation = 0
        def dump_tokens():
            with open("debug/tokens_parseados", "w") as arq:
                arq.write(tokens_lidos)

        if token is None:
            token = self.token
        # Inicializacao da pilha
        self.pilha.clear()
        self.pilha.push("$")
        self.pilha.push(self.gramatica.inicial)

        # Leitura do token
        token_analisado, token_valor = None, None
        token_analisado, token_valor = next(token)
        tokens_lidos = token_analisado

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
                lista_derivacoes.append((token_analisado, token_valor))
                self.pilha.pop()
                try:
                    # Leitura do tokens
                    token_analisado, token_valor = next(token)
                    # Todo resto dentro do try serve pra debug
                    tokens_lidos += (" " if not tokens_lidos[-1] in {"\t", "\n"} else "") + token_analisado
                    if token_analisado in {";", "{", "}"}:
                        if token_analisado == "{": identation += 1
                        elif token_analisado == "}": identation -= 1
                        tokens_lidos += "\n" + "\t" * max(0,identation)
                except StopIteration:
                    dump_tokens()
                    return False
            # Token no topo da pilha incorreto
            elif topo in self.gramatica.terminais:
                dump_tokens()
                return False
            # Producao inexistente
            elif self.tabela[topo][token_analisado] is None:
                dump_tokens()
                return False
            # Producao na pilha
            else:
                producao = self.tabela[topo][token_analisado]
                lista_derivacoes.append((topo, producao))
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
            dump_tokens()
            return False
        dump_tokens()
        with open(f"{self.folder}/acoes_sintaticas.txt","w") as arvore:
            for linha in lista_derivacoes:
                arvore.write(f"{linha[0]} ::= {linha[1]}\n")
        return True

    # Gera palavras 100 palavras aleatorias a partir da gramatica e faz o parsgin delas
    def validate(self, gramatica_original):
        total = 100
        done = set()
        with open("debug/validation_words", "w") as _: pass
        with open("debug/validation_words", "a") as arq_val:
            for _ in range(total * 100):
                if len(done) >= total: break
                sentenca: str = gramatica_original.generate_word(100)
                if not sentenca is None and sentenca not in done:
                    done.add(sentenca)
                    arq_val.write(sentenca + "\n")
                    driver = TokenDriver(sentenca.split())
                    if not self.parse(token=driver.gerador()):
                        raise SyntaxError(f"Parseei errado uma sentenca gerada pela minha propria gramatica: {sentenca}")
            else:
                print("Nao consegui formar palavras o suficiente")
        print(f"Validacao de {len(done)} sentencas completo!")

if __name__ == "__main__":
    pasta = "q1"
    driver = TokenDriver("None".split())
    try:
        parser = AnalisadorSintatico("q1", driver, True)
        parser = AnalisadorSintatico("nd", driver, True)
    except Exception as e:
        raise Exception(f"O problema foi nas que funcionam: {e}")
    parser = AnalisadorSintatico("compiladores", driver, True)
    # print(parser.parse(True, TokenDriver("c c c c c $".split()).gerador(),))
