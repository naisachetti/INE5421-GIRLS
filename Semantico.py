class FiltroSemantico:
    def __init__(self, folder: str, sdt_filename: str):
        self.derivation_dict = {}
        current_key = None
        with open(f"{folder}/{sdt_filename}") as sdt:
            for linha in sdt:
                if linha == "\n": continue
                if linha[0] == "\\":
                    sintatica_anotada: str = self.derivation_dict[current_key]
                    id = linha.split()[0][1:]
                    nova = sintatica_anotada.replace(f"\\{id}", "\\"+ '@'.join(linha.split()[1:]))
                    self.derivation_dict[current_key] = nova
                    continue
                current_key = " ".join(filter(lambda e: e[0] != "\\", linha.split()))
                self.derivation_dict[current_key] = " ".join(linha.split())
    
    def annotate_production(self, production: str):
        if not production in self.derivation_dict.keys():
            return production
        return self.derivation_dict[production]
    
    def annotate_file(self, folder: str, filename: str):
        with open(f"{folder}/{filename}", "r") as acoes_sintaticas,\
              open(f"{folder}/acoes_anotadas.txt", "w") as acoes_sintaticas_anotadas:
            for producao in acoes_sintaticas:
                acoes_sintaticas_anotadas.write(self.annotate_production(producao.strip())+"\n")

class ExpressionNode:
    def __init__(self, tipo: str, valor: str) -> None:
        self.tipo = tipo
        self.valor = valor
        self.left = None
        self.right = None

class SintaticNode:
    def __init__(self, label, parent, lista_derivacoes: list, terminais: list, eh_nt = True, eh_acao_semantica = False) -> None:
        # Atributos do nodo pertinentes para arvore de expressao
        self.node = None
        self.left_node = None
        self.right_node = None
        self.op = None
        self.lex_val = None

        # Atributos de derivacao
        self.label = label
        self.parent = parent
        self.eh_nt: bool = eh_nt
        self.eh_acao_semantica: bool = eh_acao_semantica
        self.filhos = []

        # Nodo representa um terminal
        if not self.eh_nt and not self.eh_acao_semantica:
            derivacao = lista_derivacoes.pop(0)
            terminal, valor = derivacao.split(" ::= ")
            if terminal != self.label:
                raise SyntaxError(f"Lista de derivacoes incoerentes {nao_terminal} e {self.label}")
            # Terminais sem valor como for, + e >=
            if terminal != valor:
                self.lex_val = valor
            # Terminais com valor
        
        # Nodo representa um nao terminal
        elif self.eh_nt:
            derivacao = lista_derivacoes.pop(0)
            nao_terminal, producao = derivacao.split(" ::= ")

            if not self.parent is None:
                print(f"Node: {nao_terminal} -- Pai: {self.parent.label} -- Filhos: {producao}")
            else:
                print(f"Node: {nao_terminal} -- Root -- Filhos: {producao}")
            
            if nao_terminal != self.label:
                raise SyntaxError(f"Lista de derivacoes incoerentes {nao_terminal} e {self.label}")
            
            for filho in producao.strip().split():
                # acoe semantica
                if filho[0] == "\\":
                    pass
                # terminal
                elif filho in terminais:
                    self.filhos.append(SintaticNode(filho, self, lista_derivacoes, terminais, nt=False))
                # nao terminal
                else:
                    self.filhos.append(SintaticNode(filho, self, lista_derivacoes, terminais))

class ArvoreDerivacoes:
    def __init__(self, acoes_anotadas: str, terminais: list):
        
        # Lista de derivacoes
        self.derivacoes = []
        with open(f"{acoes_anotadas}", "r") as arq:
            for linha in arq:
                self.derivacoes.append(linha.strip())
        
        self.root = Node(self.derivacoes[0].split()[0], None, self.derivacoes, terminais)

FiltroSemantico("compiladores","sdt_eu_acho").annotate_file("compiladores","acoes_sintaticas.txt")
with open("debug/terminais.txt", "r") as arq:
    terminais = arq.readline().split()
ArvoreDerivacoes("compiladores/acoes_anotadas.txt", terminais)