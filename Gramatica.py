from random import randrange


class Gramatica:

    def __init__(self) -> None:
        
        # Cria uma gramatica vazia
        self.inicial = None
        self.terminais = []
        self.nao_terminais = []

        # As producoes sao dicionarios provavelmente ainda n pensei 100% nisso
        self.producoes = {}

    # Le a gramatica de um arquivo
    def from_file(self, filename: str):
        with open(filename, "r") as arquivo:
            for linha in arquivo:
                nao_terminal, producoes = [palavra.strip() for palavra in linha.split("->")]
                
                # Simbolo inicial da gramatica
                if self.inicial == None:
                    self.inicial = nao_terminal
                
                # Adiciona nao terminal na lista
                if not nao_terminal in self.nao_terminais: self.nao_terminais.append(nao_terminal)
                
                producoes = [palavra.strip() for palavra in producoes.split("|")]
                # Criacao dos dicionarios
                self.producoes[nao_terminal] = producoes

                # Leitura de todos os simbolos novos
                for producao in producoes:
                    for simbolo in producao:

                        # TODO: Deve haver algum jeito melhor de diferenciar terminal e nao terminal
                        if simbolo == simbolo.lower():
                            if not simbolo in self.terminais: self.terminais.append(simbolo)
                        else:
                            if not simbolo in self.nao_terminais: self.nao_terminais.append(simbolo) 
        return self

    # Escreve a gramatica num arquivo
    def to_file(self, filename: str):
        with open(filename, "w") as arquivo:
            for nao_terminal, producoes in self.producoes.items():
                producoes = " | ".join(producoes)
                arquivo.write(f"{nao_terminal} -> {producoes}")

    # Simplesmente retorna uma producao aleatoria dentre as possiveis
    def random_production(self, nao_terminal: str) -> str:
        producao = self.producoes[nao_terminal][randrange(len(self.producoes[nao_terminal]))]
        if producao == "&":
            return ""
        else:
            return producao

    # Gera uma palavra aleatoria da gramatica
    def generate_word(self):
        forma_sentencial = self.inicial

        # Ao inves de um while eh um for com limite de 100 iteracoes pra n ir pra sempre
        for _ in range(100):
            for simbolo in forma_sentencial:
                if simbolo in self.nao_terminais:
                    indice = forma_sentencial.index(simbolo)
                    forma_sentencial = forma_sentencial[:indice] + self.random_production(simbolo) + forma_sentencial[indice+1:]
                    break
            else:
                break
        return forma_sentencial


g = Gramatica().from_file("gramatica_exemplo.txt")
g.to_file("output.txt")
# for _ in range (20):
#     print(g.generate_word())