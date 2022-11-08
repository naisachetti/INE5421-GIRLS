from enum import auto

class Automato:
    def __init__(self, filename: str) -> None:
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
                origem, simbolo, destino = line.strip().split(",")

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
                dict_destino = novo_estado(destino)            
                
                # Criacao da transicao
                dict_origem[simbolo] = dict_destino

        # Identificacao do estado inicial
        self.estado_inicial = [estado for estado in self.estados if estado["nome"] == inicial][0]

    def determine(self, entrada: str) -> bool:
        estado_atual = self.estado_inicial
        for simbolo in entrada:
            estado_atual = estado_atual[simbolo]
        return estado_atual["final"]


automato = Automato("automato_exemplo.txt")
assert automato.determine("bb") == True
assert automato.determine("bbbbbbbbbbbbbb") == True
assert automato.determine("ba") == False
assert automato.determine("baaaaabab") == True
assert automato.determine("aaaaaaaaaaaaaabbbbbbbbbbbbbbbbbaaaaaaa") == True
assert automato.determine("abb") == False