# Biblioteca para leitura e tratamento de arquivos contendo uma ou multiplas regex e definicoes regulares.
import string
from Pilha import *

# Le a regex e definicoes regulares em notacao infixada a partir de um arquivo.
# Retorna a mesma regex com as definicoes regulares ja substituidas em si e em notacao prefixada.
def read_regex(filename):
    letras = list(string.ascii_lowercase)
    regdefs:dict[str, str] = {}
    regexes:dict[str, str] = {}

    # Leitura da regex e definicoes regulares
    with open(filename, "r") as arquivo:
        for linha_read in arquivo:
            linha_list = linha_read.split()
            linha = ""
            for caracter in linha_list:
                linha += caracter
            if len(linha) > 0 and linha[0] not in ['#']:
                # Se é uma definicao regular
                if linha[0] not in ['>']:
                    # Verifica se a definicao regular comeca com uma letra e nao eh nomeada com apenas uma letra
                    if linha[0] in letras:
                        buffer = ""
                        for char in linha:
                            if char != ':':
                                buffer += char
                            else:
                                if len(buffer) > 1:
                                    regdef = linha[len(buffer)+1 : len(linha)]
                                    regdefs[buffer] = regdef
                                else:
                                    raise RuntimeError("Definição regular com formato incorreto. Não deve ser nomeada com apenas uma letra.")
                    else:
                        raise RuntimeError("Definição regular com formato incorreto. Deve começar com letra.")
                # Se nao eh uma definicao regular, mas sim uma ER
                else:
                    buffer = ""
                    separador = linha.find(':')
                    regexes[linha[1:separador]] = linha[separador+1:]
                    #for char in linha:
                     #   if char == '>':
                      #      pass
                       # elif char != ':':
                        #    buffer += char
                       # else:
                        #    regexes[buffer] = linha[len(buffer)+2 : len(linha)]
                            #if len(buffer) > 1:
                            #    regexes[buffer] = linha[len(buffer)+2 : len(linha)]
                            #else:
                            #    raise RuntimeError("Definição regular com formato incorreto. Não deve ser nomeada com apenas uma letra.")

    # Transforma as regex lidas em notacao infixada, com definicoes regulares, definicoes de
    # sequencias e com concatenacoes implicitas em uma regex em notacao prefixada, com definicoes
    # regulares e definicoes de sequencias substituidas e sem concatenacoes implicitas.
    regexes_prefix: dict[str, str] = {}
    for nome_regex in regexes.keys():
        regex = regexes[nome_regex]
        aux_regex = substitui_regdefs(regdefs, regex)
        aux_regex2 = adiciona_sequencias(aux_regex)
        aux_regex3 = protege_literais(aux_regex2)
        aux_regex4 = adiciona_concat_implicitas(aux_regex3)
        regex_prefix = infix_to_prefix(aux_regex4)
        regexes_prefix[nome_regex] = regex_prefix

    return regexes_prefix

# Substitui as definicoes regulares dentro da regex.
# Retorna a regex passada como parametro sem definicoes regulares a ser resolvidas.
# Exemplo: Com letras_: a | b | c, "(letras_ | 0)" vira "((a | b | c) | 0)".
def substitui_regdefs(regdefs, regex_):
    # Substitui todas as definicoes regulares que forem possiveis em uma passada
    # pela regex e, caso substituicoes tenham sido realmente feitas, analisa a nova regex.
    # Este processo se repete ate que nao haja mais definicoes regulares na regex
    regex = regex_+" "
    new_regex = regex
    while True:
        regex = new_regex
        buffer = ""
        index_i = 0
        inc_i = 0 # Para fazer a substituicao de todas as definicoes regulares possiveis em apenas uma passada.
        for i in range (len(regex)):
            # A cada simbolo especial (listado), verifica se uma definicao regular foi encontrada.
            if (new_regex[i+inc_i] in ['(',')','.','+','*','|','?',' ']) or (i == len(regex)-1):
                # Se uma definicao regular foi encontrada
                if (len(buffer) > 1) and (buffer in regdefs.keys()):
                    new_regex = new_regex[0:index_i] + '(' + regdefs[buffer] + ')' + new_regex[i+inc_i:len(new_regex)]
                    inc_i += len(regdefs[buffer])-len(buffer)-1
                    buffer = ""
                # Se nao foi ("alarme falso").
                else:
                    buffer = ""
            # Se nao apenas coloca caracter em um buffer
            else:
                if len(buffer) == 0:
                    index_i = i+inc_i
                buffer += new_regex[i+inc_i]

        # Se nenhuma substituicao foi feita na ultima passada, nao ha mais def. regulares na regex.
        if new_regex == regex:
            break

    return new_regex

# Adiciona sequencias de numeros ou letras do tipo [A-Za-z] e [0-9].
# Retorna a regex passada como parametro com as sequencias adicionadas.
# Exemplo: "[a-bA-C]+[2-4]" vira "((a|b)|(A|B|C))+((2|3|4))".
def adiciona_sequencias(regex):
    inc_i = 0 # Para fazer a adicao em apenas uma passada pela string
    init_i = 0
    new_regex = regex
    for i in range (len(regex)):
        # Achou uma definicao de sequencia
        if new_regex[i+inc_i] == '[':
            # Checa se '[' é literal, se for, ignora.
            if (i+inc_i-1 >= 0) and (new_regex[i+inc_i-1] == '\\'):
                continue

            if (i+inc_i+2 < len(new_regex)) and (new_regex[i+inc_i+1:i+inc_i+3] == 's]'):
                caracteres = list(string.printable)[62:-6]
                seq_add = ""
                index_init = i+inc_i
                init_i = i+inc_i
                # Monta sequencia de caracteres a ser inserida na regex.
                seq_add += '('
                for char in caracteres:
                    seq_add += '\\'+char+'|'
                seq_add = seq_add[:-1]
                seq_add += ')'

                # Adiciona sequencia a regex
                seq_add = '(' + seq_add + ')'
                index_end = init_i+1
                new_regex = new_regex[0:index_init] + seq_add + new_regex[index_end+2:len(new_regex)]
                inc_i += len(seq_add)-(index_end-index_init)-2
            else:             
                seq_add = ""
                index_init = i+inc_i
                init_i = i+inc_i
                while new_regex[init_i+1] != ']':
                    seq_init = new_regex[init_i+1]
                    seq_end = new_regex[init_i+3] # Motivo da verificação "if init_i+3 >= len(new_regex)"

                    # Verifica se caracteres sao do mesmo tipo e se o caracter de inicio e fim estao na ordem correta
                    # Caso isso se verifique, retorna uma lista de caracteres do tipo em questao.
                    caracteres = []
                    #if new_regex == "[char]":
                    #    caracteres = [chr(i) for i in range(0x0021, 0x1EFF)]
                    if seq_init.isupper() and seq_end.isupper() and seq_init < seq_end:
                        caracteres = list(string.ascii_uppercase)
                    elif  seq_init.islower() and seq_end.islower() and seq_init < seq_end:
                        caracteres = list(string.ascii_lowercase)
                    elif seq_init.isdigit() and seq_end.isdigit() and seq_init < seq_end:
                        caracteres = list(string.digits)
                    else:
                        raise RuntimeError("Erro. Regex mal formada. Sequência de letras ou dígitos inválida.")

                    # Monta sequencia de caracteres a ser inserida na regex.
                    if len(seq_add) > 0:
                        seq_add += '|('
                    else:
                        seq_add += '('
                    for char in caracteres:
                        if char >= seq_init and char <= seq_end:
                            seq_add += char+'|'
                    seq_add = seq_add[:-1]
                    seq_add += ')'

                    # Para suportar definicoes de sequencias do tipo [A-Za-z], e não somente [A-Z] ou [a-z]
                    init_i += 3

                    # Para prevenir acesso a indices inexistentes na string por conta do nao fechamento da
                    # definicao de sequencias, com ']'.
                    if (init_i+3) >= len(new_regex):
                        raise RuntimeError("Erro. Regex mal formada. Sequência de letras ou dígitos inválida.")

                # Adiciona sequencia a regex
                seq_add = '(' + seq_add + ')'
                index_end = init_i+1
                new_regex = new_regex[0:index_init] + seq_add + new_regex[index_end+1:len(new_regex)]
                inc_i += len(seq_add)-(index_end-index_init)-1
    
    return new_regex


# Coloca literais entre parenteses. Assim, "protege" literais da adicao de concatenacoes implicitas indevidas.
# Retorna a regex passada como parametro com os literais entre parenteses.
# Exemplo: "abc\++" vira "abc(\+)+".
def protege_literais(regex):
    inc_i = 0 # Para fazer a protecao em apenas uma passada pela string
    new_regex = regex
    for i in range (len(regex)):
        if new_regex[i+inc_i] == '\\':
            new_regex = new_regex[0:i+inc_i] + '(' + new_regex[i+inc_i:i+inc_i+2] + ')' + new_regex[i+inc_i+2:len(new_regex)]
            inc_i += 2

    return new_regex

# Adiciona concatenacoes implicitas.
# Retorna a regex passada como parametro somente com concatenacoes explicitas.
# Exemplo: "ab*c(\+)d" vira "a.b*.c.(\+).d".
def adiciona_concat_implicitas(regex):
    inc_i = 0 # Para fazer a adicao em apenas uma passada pela string
    new_regex = regex
    for i in range (len(regex)):
        if new_regex[i+inc_i] not in [')','.','+','*','|','?',' ','\\']:
            k = i+inc_i-1
            while (k >= 0) and new_regex[k] == ' ':
                k -= 1
            if (k >= 0) and (new_regex[k] not in ['(','.','|']) and (i+inc_i-1 >= 0) and (new_regex[i+inc_i-1] != '\\'):
                new_regex = new_regex[0:k+1] + '.' + new_regex[k+1:len(new_regex)]
                inc_i += 1

    return new_regex

# Transforma a regex em notacao infixada para notacao prefixada.
# Retorna a versao prefixada da regex passada como parametro.
# Exemplo: "(a | b)*" vira "*|ab".
# Algoritmo retirado de: https://www.geeksforgeeks.org/convert-infix-prefix-notation/
def infix_to_prefix(regex):
    # Definicao das ordens de precedencia e associatividade para os operadores
    prec_op = {'*':3, '+':3, '?':3, '.':2, '|': 1}
    assoc_op = {'*':"direita,", '+':"direita", '?':"direita", '.':"esquerda", '|':"esquerda"}

    # Inverte regex infixada original
    regex_invertida = ""
    aux_regex_invertida = regex[::-1]
    # Troca os parenteses, exceto se forem literais
    is_literal = False
    for i in range (len(aux_regex_invertida)):
        if aux_regex_invertida[i] == '(':
            # Checa se ')' eh um literal
            if i < len(aux_regex_invertida)-1 and aux_regex_invertida[i+1] == '\\':
                # Checa se o proprio \ eh um literal.  Se for, ')' não é um literal e deve ser invertido.
                if i < len(aux_regex_invertida)-2 and aux_regex_invertida[i+2] == '\\':
                    regex_invertida += ')'
                else:
                    regex_invertida += '('
            else:
                regex_invertida += ')'
        elif aux_regex_invertida[i] == ')':
            # Checa se '(' eh um literal
            if i < len(aux_regex_invertida)-1  and aux_regex_invertida[i+1] == '\\':
                # Checa se o proprio \ eh um literal. Se for, '(' não é um literal e deve ser invertido.
                if i < len(aux_regex_invertida)-2 and aux_regex_invertida[i+2] == '\\':
                    regex_invertida += '('
                else:
                    regex_invertida += ')'
            else:
                regex_invertida += '('
        else:
            regex_invertida += aux_regex_invertida[i]

    # Converte regex infixada invertida para uma regex posfixada.
    # Para maiores detalhes sobre o algoritmo, ver referência na assinatura desta funcao.
    operadores = Pilha()
    regex_inv_posf = ""
    is_literal = False
    for i in range(len(regex_invertida)):
        char = regex_invertida[i]
        if char not in ['(',')','*','+','?','.','|',' ']:
            regex_inv_posf += char
        elif char == ' ':
            # Verifica se simbolo especial eh literal. O que eh invalido neste caso.
            is_literal = True if (i < len(regex_invertida)-1 and regex_invertida[i+1] == '\\') else False
            barra_is_literal = True if (i < len(regex_invertida)-2 and regex_invertida[i+2] == '\\') else False
            # Caso seja
            if is_literal and not barra_is_literal:
                raise RuntimeError("Erro. Regex mal formada. Literal inválido.")
            # Caso nao seja
            pass
        elif char == '(':
            # Verifica se simbolo especial eh literal
            is_literal = True if (i < len(regex_invertida)-1 and regex_invertida[i+1] == '\\') else False
            barra_is_literal = True if (i < len(regex_invertida)-2 and regex_invertida[i+2] == '\\') else False
            # Caso seja
            if is_literal and not barra_is_literal:
                regex_inv_posf += char
                is_literal = False
            # Caso nao seja
            else:
                operadores.push('(')
        elif char == ')':
            # Verifica se simbolo especial eh literal
            is_literal = True if (i < len(regex_invertida)-1 and regex_invertida[i+1] == '\\') else False
            barra_is_literal = True if (i < len(regex_invertida)-2 and regex_invertida[i+2] == '\\') else False
            # Caso seja
            if is_literal and not barra_is_literal:
                regex_inv_posf += char
                is_literal = False
            # Caso nao seja
            else:
                operador = operadores.pop()
                while operador != '(':
                    regex_inv_posf += operador
                    operador = operadores.pop()
        # Simbolo eh potencialmente um operador
        else:
            # Verifica se simbolo especial eh literal
            is_literal = True if (i < len(regex_invertida)-1 and regex_invertida[i+1] == '\\') else False
            barra_is_literal = True if (i < len(regex_invertida)-2 and regex_invertida[i+2] == '\\') else False
            # Caso seja
            if is_literal and not barra_is_literal:
                regex_inv_posf += char
                is_literal = False
            # Caso nao seja
            else:
                if operadores.size() == 0 or operadores.top() == '(':
                    operadores.push(char)
                else:
                    if char == operadores.top():
                        if assoc_op[char] == "direita":
                            operadores.push(char)
                        else:
                            regex_inv_posf += operadores.pop()
                            operadores.push(char)
                    else:
                        operador = operadores.top()
                        while (operadores.size() > 0) and (operador != '(') and (prec_op[operador] >= prec_op[char]):
                            regex_inv_posf += operadores.pop()
                            operador = operadores.top()
                        operadores.push(char)

    while operadores.size() > 0:
        regex_inv_posf += operadores.pop()

    # Inverte regex posfixada, obtendo uma regex prefixada da regex infixada original
    regex_pref = regex_inv_posf[::-1]

    return regex_pref
