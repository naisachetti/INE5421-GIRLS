linha = "ab<CD>e<F>ghij<KLMNOP>"
delimiters = "<>"
nt_separados = []
start = 0
for i, caracter in enumerate(linha):
    in_nt = False
    if caracter == delimiters[0] and i:
        nt_separados.append(linha[start:i])
        start = i
    if caracter == delimiters[1]:
        nt_separados.append(linha[start:i+1])
        start = i+1
else:
    if nt_separados[-1][-1] != linha[-1]:
        nt_separados.append(linha[start:])

tudo_separado = []
for grupo in nt_separados:
    if delimiters[0] in grupo or delimiters[1] in grupo:
        tudo_separado.append(grupo)
    else:
        for letter in grupo:
            tudo_separado.append(letter)
print(tudo_separado[0])
