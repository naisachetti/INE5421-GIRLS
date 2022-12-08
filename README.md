## Como usar o GIRLS (Gerador IRado de analisador Léxico e Sintático)

Acompanhe este documento com os arquivos de exemplo da pasta "pasca".

1) Crie uma pasta com o nome do seu projeto (ex.: pasca)
2) Nesta pasta, crie três arquivos:
    - tokens: Expressões regulares para os tokens da linguagem (Veja a seção "Arquivo de tokens").<br>
    - grammar: Gramática da linguagem (Veja a seção "Arquivo de gramática").<br>
    - program: Código fonte do programa a ser analisado.<br>
3) Rode o GIRLS com o seguinte comando, em um terminal dentro da pasta INE5421-GIRLS:

```
$ python3 GIRLS.py <nome_da_pasta_do_projeto>
```

## Arquivo de tokens

O arquivo de tokens deve ter a seguinte estrutura, com definições regulares antes de expressões regulares que representam tokens:

```
# Comentários podem ser feitos com a utilização de # no início de uma linha

abece: (a | b | c)*
simbolos: \\+ | !

# Expressões regulares que representam tokens devem ser indicadas com > no início da linha
>token1: abece | bba
>token2: b.ba* | &
>token3: simbolos | &

```

**IMPORTANTE:** Tokens não devem conter outros tokens em sua definição.

**IMPORTANTE 2:** Tokens mais específicos devem ser definidos antes de tokens menos específicos. Veja o exemplo:

```
# "begin" se encaixa tanto como o tipo "begin", como "id", mas queremos que seja interpretado como
# "begin", então precisa ser declarado antes.
>begin:begin
>id:letters(letters|numbers)*

```

### Operadores

Os operadores suportados são:
- \* : Fecho
- \+ : Fecho positivo
- ? : Talvez
- | : Ou
- . : Concatenação
    
    

### Definições de sequências

Definições de sequências são feitas da seguinte forma:

```
letras_minusculas: [A-Z]
letras_maiusculas: [a-z]
letras_minu_maiu: [D-Gt-z]
numeros: [0-9]

# E podem ser definidas diretamente nos tokes também
>token: letras_minusculas* | [d-t] ? | [7-9]

```

### Literais

Para a definição de literais apenas coloque \ na frente dos operadores. Exemplo:


Definições de sequências são feitas da seguinte forma:

```
# \| será interpretado como | e \\ como \
>token: letras_minusculas* \| [d-t] ? | [7-9] | \\
```


## Arquivo de gramática

O arquivo onde está definida a gramática deve estar no seguinte formato, no qual:

- Símbolos não terminais devem estar à esquerda de "::=" suas produções à direita.
- As produções de um mesmo não terminal precisam estar todas juntas, separadas por |.
- Os símbolos não terminais devem estar deparados por espaço.

Veja o exemplo:

```
P ::= begin D C end
D ::= inteiro id I
I ::= , id I | &
C ::= C ; T = E | T = E | com
E ::= E + T | T
T ::= id | id [ E ]

```