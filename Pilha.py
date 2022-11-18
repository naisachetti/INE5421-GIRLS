class Pilha:

    # Cria uma pilha vazia
    def __init__(self):
        self.elementos = []
    
    # Insere um elemento no topo da pilha
    def push(self, elemento):
        self.elementos.append(elemento)

    # Retira e retorna o elemento do topo da pilha
    def pop(self):
        return self.elementos.pop()

    # Retorna o elemento do topo da pilha, sem retira-lo
    def top(self):
        if self.size() > 0:
            return self.elementos[self.size()-1]
        else:
            return None

    # Retorna o número de elementos contido na pilha
    def size(self):
        return len(self.elementos)