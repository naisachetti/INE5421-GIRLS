from enum import auto

class Automato:
    def __init__(self, filename: str) -> None:
        self.estados: dict[Estado] = {}
        with open(filename, "r") as arquivo:
            self.n_estados: int = int(arquivo.readline().strip())
            self.estado_inicial: Estado = Estado(arquivo.readline().strip())
            self.estados_finais: list[Estado] = [Estado(nome) for nome in arquivo.readline().strip().split(",")]
            self.alfabeto: list[str] = arquivo.readline().strip().split(",")
            for line in arquivo:
                origin_str, simbol, destiny_str = line.strip().split(",")

                # Criacao dos estados na tansicao caso eles ainda nao existam
                if not origin_str in self.estados:
                    self.estados[origin_str] = Estado(origin_str)
                if not destiny_str in self.estados:
                    self.estados[destiny_str] = Estado(destiny_str)
                
                # Criacao da transicao
                self.estados[origin_str].add_trans(simbol, self.estados[destiny_str])

    def __repr__(self):
        saida = f"inicial: {self.estado_inicial.id}\n"
        saida += "finais: "+" ".join([estado.id for estado in self.estados_finais])+"\n"
        saida += "simbolos: "+" ".join(self.alfabeto)+"\n"
        saida += "estados: "+" ".join([estado.id for estado in self.estados.values()])+"\n"
        saida += "transicoes:\n"
        for estado in self.estados.values():
            saida += f"{estado}\n"
        return saida

class Estado:
    def __init__(self, id: str) -> None:
        self.id = id
        self.transicoes = {}
    
    def add_trans(self, simbol: str, state) -> None:
        self.transicoes[simbol] = state

    def __repr__(self) -> str:
        saida = f"{self.id} ->\t"
        for simbol, state in self.transicoes.items():
            saida += f"{simbol}:{state.id}\t"
        return saida


automato = Automato("automato_exemplo.txt")
print(automato)