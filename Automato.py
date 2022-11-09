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

    # Representacao do automato ao ser impresso
    def __repr__(self) -> str:
        saida = f"n estados: {self.n_estados}\n"
        saida += f"estado inicial: "+self.inicial["nome"]+"\n"
        saida += f"estados finais: "+",".join(self.finais)+"\n"
        saida += f"alfabeto: "+",".join(self.alfabeto)+"\n"
        for estado in self.estados:
            for simbolo in self.alfabeto:
                if isinstance(estado[simbolo], dict) and estado[simbolo]["nome"] != "Morto":
                    saida += estado["nome"]+": "+simbolo+" -> "+estado[simbolo]["nome"]+"\n"
                elif isinstance(estado[simbolo], list):
                    saida += estado["nome"]+": "+simbolo+" -> "
                    saida += "-".join([est["nome"] for est in estado[simbolo]])+"\n"
        return saida
 
    # Recebe uma entrada e retorna se o automato a reconhece
    def reconhece(self, entrada: str) -> bool:
        estado_atual = self.inicial
        for simbolo in entrada:
            estado_atual = estado_atual[simbolo]
            if isinstance(estado_atual, set):
                raise RuntimeError ("Transicao nao deterministica")
        return estado_atual["final"]
    
    # Recebe outro automato e retorna a uniao entre os dois
    def uniao_com(self, other):
        uniao = Automato(None)
        copia = self.copy()
        other = other.copy()

        uniao.n_estados = copia.n_estados + other.n_estados + 1

        # Identifica o estado morto da copia e do outro e transfere o do outro para o da copia
        morto_copia = [estado for estado in copia.estados if estado["nome"] == "Morto"][0]
        morto_other = [estado for estado in other.estados if estado["nome"] == "Morto"][0]
        for estado in other.estados:
            for simbolo in other.alfabeto:
                if estado[simbolo]["nome"] == "Morto":
                    estado[simbolo] = morto_copia
        other.estados.remove(morto_other)
        
        # Cria o novo alfabeto e inclui &
        uniao.alfabeto = list(dict.fromkeys(copia.alfabeto+other.alfabeto+["&"]))
        
        # Cria transicoes vazias nos automatos que serao unidos para os simbolos especificados
        def transicao_vazia(automato, alfabeto):
            for simbolo in alfabeto:
                if not simbolo in automato.alfabeto:
                    for estado in automato.estados:
                        estado[simbolo] = morto_copia
        transicao_vazia(copia, uniao.alfabeto)
        transicao_vazia(other, uniao.alfabeto)

        # Muda o nome dos estados do outro automato
        for estado in other.estados:
            estado["nome"] += "_"
        other.finais = [outro + "_" for outro in other.finais]
        uniao.finais = copia.finais + other.finais

        # Cria o estado inicial que vai por epslon para os outros iniciais e pra nenhum mais
        uniao.inicial = {"nome": "inicio_uniao", "final": False, "&": [copia.inicial, other.inicial]}
        for simbolo in uniao.alfabeto:
            if simbolo == "&":
                continue
            uniao.inicial[simbolo] = morto_copia

        # Une de fato os estados
        uniao.estados = [uniao.inicial] + copia.estados + other.estados
        
        return uniao

    # Exporta o arquivo do automato
    def export(self, filename: str):
        with open(filename, "w") as arquivo:
            arquivo.write(f"{self.n_estados}\n")
            arquivo.write(self.inicial["nome"]+"\n")
            arquivo.write(",".join(self.finais)+"\n")
            arquivo.write(",".join(self.alfabeto)+"\n")
            for estado in self.estados:
                for simbolo in self.alfabeto:
                    if isinstance(estado[simbolo], dict) and estado[simbolo]["nome"] != "Morto":
                        arquivo.write(estado["nome"]+": "+simbolo+" -> "+estado[simbolo]["nome"]+"\n")
                    elif isinstance(estado[simbolo], list):
                        arquivo.write(estado["nome"]+": "+simbolo+" -> ")
                        arquivo.write("-".join([est["nome"] for est in estado[simbolo]])+"\n")

a = Automato("unido_a.txt")
b = Automato("unido_b.txt")
ab = a.uniao_com(b)
ab.export("exportado.txt")
# ab.export("exportado.txt")