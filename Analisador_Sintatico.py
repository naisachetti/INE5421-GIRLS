from Gramatica import Gramatica
from Pilha import Pilha

# TODO: VERIFICAR SE A GRAMATICA EH LL1

class TokenDriver:
    def __init__(self, tokens_validos: list) -> None:
        self.tokens = tokens_validos
    
    def gerador(self):
        for element in self.tokens:
            yield element
            
class ParsingTable:
    def __init__(self, gramatica: Gramatica) -> None:
        terminais = gramatica.terminais.copy()
        terminais += "$"
        firstpos = gramatica.firspost()
        followpos = gramatica.followpost()
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
                            raise RuntimeError(f"Tentei colocar duas producoes na tabela ll1 {nt} {terminal}")
                        self.table[nt][terminal] = producao
                    continue

                # Preenchimento de first
                first = gramatica.first_prod(producao)
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

class AnalisadorSintatico:
    def __init__(self, gramatica: Gramatica) -> None:
        # self.gramatica = gramatica.sem_recursao().fatorada().sem_inalcancaveis()
        self.gramatica = gramatica
        self.tabela = ParsingTable(self.gramatica)
        self.pilha = Pilha()
    
    def parse(self, codigo_fonte: str):
        # Inicializacao da pilha
        self.pilha.clear()
        self.pilha.push("$")
        self.pilha.push(self.gramatica.inicial)

        token_analisado = None
        token = TokenDriver([caracter for caracter in "(i)+(i*(i))$"]).gerador()
        token_analisado = next(token)

        topo = self.pilha.top()
        while topo != "$":
            print(topo, token_analisado, self.pilha, end=" ")
            # Token no topo da pilha correto
            if topo == token_analisado:
                print(topo)
                self.pilha.pop()
                token_analisado = next(token)
            # Token no topo da pilha incorreto
            elif topo in self.gramatica.terminais:
                raise SyntaxError("Erro de Sintaxe no arquivo fonte (Essa msg eh do trabalho)")
            # Producao inexistente
            elif self.tabela[topo][token_analisado] is None:
                raise SyntaxError("Erro de Sintaxe no arquivo fonte (Essa msg eh do trabalho)")
            # Producao na pilha
            else:
                producao = self.tabela[topo][token_analisado]
                print(producao)
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
        print("SINTAXE PERFEITA")

if __name__ == "__main__":
    g = Gramatica().from_file("gramatica_precedente.txt").tratada()
    parser = AnalisadorSintatico(g)
    print(parser.tabela)
    parser.parse(None)
