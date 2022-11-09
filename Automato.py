from enum import auto
from re import S


class Automato:
    
    # Cria o automato
    def __init__(self, filename: str or None) -> None:
        
        # Cria um automato vazio se nao receber arquivo
        if filename is None:
            self.estados = None
            self.n_estados = None
            self.finais = None
            self.inicial = None
            self.alfabeto = None
            return
        
        self.estados: list[dict] = []
        with open(filename, "r") as arquivo:
            
            # Leitura do cabecalho
            self.n_estados: int = int(arquivo.readline().strip())
            inicial: str = arquivo.readline().strip()
            self.finais: str = arquivo.readline().strip().split(",")
            self.alfabeto: list[str] = arquivo.readline().strip().split(",")
            
            # Criacao do estado morto
            morto: dict = {"nome": "Morto", "final": False}
            for simbolo in self.alfabeto:
                morto[simbolo] = morto
            self.estados.append(morto)
            
            # Criacao de todos os estados e suas transicoes
            for line in arquivo:
                # Leitura da linha
                origem, simbolo, destinos = line.strip().split(",")
                destinos = list(destinos.split("-")) # Nao Determinismo

                # Criacao dos estados na tansicao caso eles ainda nao existam
                def novo_estado(nome: str):
                    if not nome in [estado["nome"] for estado in self.estados]:
                        estado = {"nome": nome, "final": nome in self.finais}
                        for simbolo in self.alfabeto:
                            estado[simbolo] = morto
                            self.estados.append(estado)
                            return estado
                    return [estado for estado in self.estados if estado["nome"] == nome][0]
                dict_origem = novo_estado(origem)

                # Transicao Deterministica
                if len(destinos) == 1:
                    dict_destino = novo_estado(destinos[0])
                
                # Transicao Nao Deterministica
                else:
                    dict_destino = {novo_estado(destino) for destino in destinos}        
                
                # Criacao da transicao
                dict_origem[simbolo] = dict_destino

        # Identificacao do estado inicial
        self.inicial = [estado for estado in self.estados if estado["nome"] == inicial][0]

    # Retorna uma copia do automato
    def copy(self):
        copia = Automato(None)
        copia.alfabeto = self.alfabeto.copy()
        copia.finais = self.finais.copy()
        copia.n_estados = self.n_estados
        estados_copia = [estado.copy() for estado in self.estados]
        # Ajusta as referencias para que se refiram as copias nao ao original
        for estado_copia in estados_copia:
            for simbolo in copia.alfabeto:
                estado_copia[simbolo] = [estado for estado in estados_copia if estado_copia[simbolo]["nome"] == estado["nome"]][0]
        copia.estados = estados_copia
        copia.inicial = [estado for estado in estados_copia if estado["nome"] == self.inicial["nome"]][0]
        return copia

    def reconhece(self, entrada: str) -> bool:
        estado_atual = self.inicial
        for simbolo in entrada:
            estado_atual = estado_atual[simbolo]
            if isinstance(estado_atual, set):
                raise RuntimeError ("Transicao nao deterministica")
        return estado_atual["final"]
    
    def uniao_com(self, other):
        pass



# Verifica se o automato ta reconhecendo as palavras corretamente
automato = Automato("automato_exemplo.txt")

assert automato.reconhece("bb") == True
assert automato.reconhece("bbbbbbbbbbbbbb") == True
assert automato.reconhece("ba") == False
assert automato.reconhece("baaaaabab") == True
assert automato.reconhece("aaaaaaaaaaaaaabbbbbbbbbbbbbbbbbaaaaaaa") == True
assert automato.reconhece("abb") == False