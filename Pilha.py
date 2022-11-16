class Pilha:

    # Cria uma pilha vazia
    def __init__(self):
        self.elementos = []
        self.filhos_visitados = []
    
    # Insere um elemento no topo da pilha
    def push(self, elemento):
        self.elementos.append(elemento)
        self.filhos_visitados.append(0)

    # Retira e retorna o elemento do topo da pilha
    def pop(self):
        self.filhos_visitados.pop()
        return self.elementos.pop()

    # Retorna o elemento do topo da pilha, sem retira-lo
    def top(self):
        if self.size() > 0:
            return self.elementos[self.size()-1]
        else:
            return None

    # Retorna o numero de filhos visitados do nodo no topo da pilha
    def top_filhos_visitados(self):
        if self.size() > 0:
            return self.filhos_visitados[self.size()-1]
        else:
            return None

    # Incrementa o numero de filhos visitados do nodo no topo da pilha
    def top_inc_filhos_visitados(self):
        self.filhos_visitados[self.size()-1] += 1

    # Retorna o número de elementos contido na pilha
    def size(self):
        return len(self.elementos)