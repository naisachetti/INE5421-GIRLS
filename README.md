
## Como usar o WOMEN (Words Organized by Meaningful Elements and Notation)

Acompanhe este documento com os arquivos de exemplo da pasta "pasca".

1) Crie uma pasta com o nome do seu projeto (ex.: pasca)
2) Nesta pasta, crie três arquivos:
    - tokens: Expressões regulares para os tokens da linguagem (Veja a seção "Arquivo de tokens").<br>
    - grammar: Gramática da linguagem (Veja a seção "Arquivo de gramática").<br>
    - program (opcional): Código fonte do programa a ser analisado quando o atributo PROGRAM não for especificado na chamada do Makefile.<br>
3) Rode os analisadores léxico e sintático do WOMEN com o seguinte comando:

```
$ make analysis DIR=<nome_da_pasta_do_projeto> [PROGRAM=<nome do arquivo do programa>]
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
simbolos: [s]

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
- Os símbolos devem ser separados por espaço.
- Os símbolos *, +, ?, (, ) e & são definidos como literais adicionando um \ imediatamente antes deles.

Veja o exemplo:

```
TYPEDEF ::= ( int | float | string ) ident
FUNCCALL ::= ident \( ( PARAMLIST | \& ) \)
PARAMLIST ::= ident , PARAMLIST | ident
```

A gramática também pode ser descrita na forma BNF (Backus-Naur Form), como no exemplo abaixo:

```
TYPEDEF ::= ( int | float | string ) ident
FUNCCALL ::= ident \( ( PARAMLIST ) ? \)
PARAMLIST ::= ident ( , PARAMLIST ) ?
```

## Tratamento de gramáticas e debug

Antes da geração da tabela de análise sintática, o programa transforma uma gramática dada na forma BNF em uma gramática em formato convencional (sem os símbolos +, * e ?, típicos da notação) e com as seguintes características:
- Sem loops
- &-livre
- Sem produções unitárias
- Sem produções diretas 
- Sem repetições
- Sem recursão à esquerda
- Fatorada

Durante esse processo, o programa gera uma série de arquivos com as gramáticas intermediárias que podem ser úteis no processo de debug de gramáticas. Tais arquivos são armazenados na pasta "debug". Ainda, ao fazer o parsing de um código fonte, gera um arquivo chamado "tokens_parseados", na mesma pasta, com os tokens que conseguiram passar pelo parsing na mesma estrutura do código original. Isso facilita a busca por erros sintáticos no programa em questão.

