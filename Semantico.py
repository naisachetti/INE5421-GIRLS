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

class FiltroSDT:
    def __init__(self, folder: str, filename: str):
        with open(f"{folder}/{filename}") as sdt_original:
            super_string = sdt_original.read()
        producoes_anotadas = super_string.split("\n\n")
        for i, anotacoes in enumerate(producoes_anotadas):
            producao, *anotacoes = anotacoes.split("\n")
            producao_simbolos = producao.split()[2:]
            # Itera sobre os simbolos de uma anotacao
            for k, anotacao in enumerate(anotacoes):
                anotacao_simbolos = anotacao.split()
                # Itera sobre um simbolo de uma anotacao procurando match
                for j, simbolo in enumerate(anotacao_simbolos):
                    # Guarda de casos triviais
                    if simbolo[0] in {"\\", ",", "}"} or simbolo in {"None", "ExpressionNode("}: continue
                    # Simbolo simplesmente esta numa producao
                    if simbolo in producao_simbolos:
                        anotacao_simbolos[j] = f"self.filhos[{producao_simbolos.index(simbolo)}]"
                    elif simbolo.split(".")[0] in producao_simbolos:
                        anotacao_simbolos[j] = f"self.filhos[{producao_simbolos.index(simbolo.split('.')[0])}].{' '.join(simbolo.split('.')[1:])}"
                anotacoes[k] = " ".join(anotacao_simbolos)
            producoes_anotadas[i] = [producao, *anotacoes]
        
        with open(f"{folder}/sdt", "w") as arquivo:
            for producao, *anotacoes in producoes_anotadas:
                arquivo.write(producao+"\n")
                for anotacao in anotacoes:
                    arquivo.write(anotacao+"\n")
                arquivo.write("\n")

class SemanticError(SyntaxError):
    pass

class Escopo:
    def __init__(self, parent, loop = False):
        self.parent = parent
        self.loop = loop
        self.filhos = []
        self.leave = True
        self.variaveis_declaradas = []
    
    def entrar(self, loop = False):
        novo_escopo = Escopo(self, loop=loop)
        self.filhos.append(novo_escopo)
        return novo_escopo
    
    def declare(self, tipo, variavel):
        if variavel in map(lambda e: None if type(e) == Escopo else e[1], self.filhos):
            raise SemanticError(f"Redeclaracao da variavel {variavel} no mesmo escopo {self}")
        self.filhos.append((tipo,variavel))
    
    def tipo_de(self, variavel):
        variaveis = [filho for filho in self.filhos if type(filho) != Escopo]
        encontrei = list(filter(lambda e: e[1] == variavel, variaveis))
        # Procura em escopos acima
        if not len(encontrei):
            if self.parent:
                return self.parent.tipo_de(variavel)
            else:
                return None
        return encontrei[0][0]

    
    def __repr__(self):
        return "{"+" ".join(map(lambda e: repr(e), self.filhos))+"}"

escopo_global = Escopo(None)
escopo_atual = escopo_global
escopo_loop = False
ponto_e_virgula_count = None
arithmetic_starter = {"EXPRESSION", "ATRIBSTAT_AUX1"}
current_arithmetic_type = None

class ExpressionNode:
    def __init__(self, valor: str, left, right):
        # self.tipo = tipo
        self.valor = valor
        self.left_node = left
        self.right_node = right
    
    def __repr__(self):
        saida = f"expnode: [{self.valor}"
        if not self.left_node is None:
            saida += f" left: {self.left_node}"
        if not self.right_node is None:
            saida += f" right: {self.right_node}"
        return saida + "]"

class SintaticNode:
    def __init__(self, label, parent, lista_derivacoes: list, terminais: list, eh_nt = True, acao_semantica = False) -> None:
        # Atributos do nodo pertinentes para arvore de expressao
        self.node: ExpressionNode = ExpressionNode(None, None, None)
        self.lex_val = None

        # Atributos de derivacao
        self.label = label
        self.parent = parent
        self.eh_nt: bool = eh_nt
        # if self.label == "ATRIBSTAT_AUX1": acao_semantica = True
        self.acao_semantica: bool = True
        self.filhos: list[SintaticNode] = []

        # Nodo representa um terminal
        if not self.eh_nt:
            derivacao = lista_derivacoes.pop(0)
            terminal, valor = derivacao.split(" ::= ")
            if terminal != self.label:
                raise SyntaxError(f"Lista de derivacoes incoerentes {terminal} e {self.label} na linha -{len(lista_derivacoes)}")
            # Terminais com valor lexico
            self.lex_val = valor
        
        # Nodo representa um nao terminal
        else:
            derivacao = lista_derivacoes.pop(0)
            nao_terminal, producao = derivacao.split(" ::= ")
            
            if nao_terminal != self.label:
                raise SyntaxError(f"Lista de derivacoes incoerentes {nao_terminal} e {self.label} na linha -{len(lista_derivacoes)}")
            
            for filho in producao.strip().split():
                # acoe semantica
                if filho[0] == "\\":
                    # Durante a criacao da arvore sintatica acoes semanticas nao sao resolvidas
                    self.filhos.append(filho[1:].replace("@"," "))
                # terminal
                elif filho in terminais:
                    if filho != "&":
                        self.filhos.append(SintaticNode(filho, self, lista_derivacoes, terminais, eh_nt=False, acao_semantica=acao_semantica))
                # nao terminal
                else:
                    self.filhos.append(SintaticNode(filho, self, lista_derivacoes, terminais, acao_semantica=acao_semantica))

    def acoes_semanticas(self):
        print(f"{self.label} ::= {' '.join(map(lambda e: e if type(e) == str else e.label, self.filhos))}")
        global escopo_atual
        global escopo_loop
        global ponto_e_virgula_count
        global arithmetic_starter
        global current_arithmetic_type
        for filho in self.filhos:
            # exclusivamente acao semantica
            if type(filho) == str:
                if self.acao_semantica:
                    print(f"acao semantica: {filho}")
                    exec(filho)
            # filho obrigatoriamente um Nodo 
            elif filho.eh_nt:
                if filho.label in arithmetic_starter:
                    current_arithmetic_type = "no_type_yet"
                filho.acoes_semanticas()
                if filho.label in arithmetic_starter:
                    current_arithmetic_type = None
            # filho terminal
            else:
                if filho.label == "for":
                    escopo_loop = True
                    escopo_atual = escopo_atual.entrar(loop=True)
                    ponto_e_virgula_count = 0
                elif filho.label == "{":
                    ponto_e_virgula_count = None
                    if not escopo_loop:
                        escopo_atual = escopo_atual.entrar()
                    escopo_loop = False
                elif filho.label == "}" and not escopo_loop:
                    escopo_atual = escopo_atual.parent
                elif filho.label == ";" and escopo_loop and not ponto_e_virgula_count is None:
                    ponto_e_virgula_count += 1
                    if ponto_e_virgula_count >= 3:
                        ponto_e_virgula_count = None
                        escopo_loop = False
                        escopo_atual = escopo_atual.parent
                elif filho.label == "break":
                    if not escopo_atual.loop:
                        raise SemanticError("Break fora de escopo de loop")
                elif current_arithmetic_type and filho.label in {"int_constant", "float_constant", "string_constant", "ident"}:
                    if filho.label == "ident":
                        tipo = escopo_atual.tipo_de(filho.lex_val)
                        if not tipo:
                            raise SemanticError(f"Variavel nao declarada {filho.lex_val} usada numa atribuicao")
                    else:
                        tipo = filho.label.replace("_constant", "") #KKKKKKKKKKKKKKKKKKKKKK
                    if current_arithmetic_type == "no_type_yet":
                        current_arithmetic_type = tipo
                    elif tipo != current_arithmetic_type:
                        raise SemanticError(f"Expressao do tipo {current_arithmetic_type} tentou receber um {tipo}")



    
    def print_tree(self):
        print(f"{self.label} ::= {' '.join(map(lambda e: e if type(e) == str else e.label, self.filhos))}")
        for filho in self.filhos:
            # exclusivamente acao semantica
            if type(filho) == str:
                continue
            # filho obrigatoriamente um Nodo 
            elif filho.eh_nt:
                filho.print_tree()
    
    def print_exp(self):
        if self.node:
            print(f"{self.label}: {self.node}")
            print()
        for filho in self.filhos:
            # exclusivamente acao semantica
            if type(filho) == str:
                continue
            # filho obrigatoriamente um Nodo 
            elif filho.eh_nt:
                filho.print_exp()

    @property
    def left_node(self):
        return self.node.left_node
    
    @property
    def right_node(self):
        return self.node.right_node
    
    @left_node.setter
    def left_node(self, value):
        self.node.left_node = value

    @right_node.setter
    def right_node(self, value):
        self.node.right_node = value

class ArvoreDerivacoes:
    def __init__(self, acoes_anotadas: str, terminais: list):
        
        # Lista de derivacoes
        self.derivacoes = []
        with open(f"{acoes_anotadas}", "r") as arq:
            for linha in arq:
                self.derivacoes.append(linha.strip())
        
        self.root = SintaticNode(self.derivacoes[0].split()[0], None, self.derivacoes, terminais)

    def resolver_acoes_semanticas(self):
        self.root.acoes_semanticas()
    
    def print_tree(self):
        self.root.print_tree()

    def print_exp(self):
        self.root.print_exp()

if __name__ == "__main__":

    FiltroSDT("compiladores", "sdt_base")
    FiltroSemantico("compiladores","sdt").annotate_file("compiladores","acoes_sintaticas.txt")
    with open("debug/terminais.txt", "r") as arq:
        terminais = arq.readline().split()
    der = ArvoreDerivacoes("compiladores/acoes_anotadas.txt", terminais)
    print("Arvore de derivacoes montadas")
    der.resolver_acoes_semanticas()
    print("-----------")
    print(der.print_exp())
    print(repr(escopo_atual))