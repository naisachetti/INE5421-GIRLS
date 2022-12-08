from regex_lib import read_regex
from Automato import *

if __name__ == '__main__':
    filenames = ["regex_exemplo.txt", "regex_exemplo2.txt", "regex_exemplo3.txt", "regex_exemplo4.txt", "regex_exemplo5.txt",
                "regex_exemplo6.txt", "regex_exemplo7.txt", "regex_exemplo8.txt", "regex_exemplo9.txt", "regex_exemplo_volatil.txt"]

    for filename in filenames:
        regex_exemplo = read_regex(filename)
        token_types = regex_exemplo.keys()
        for tt in token_types:
            Automato().from_regex(regex_exemplo[tt], tt).to_file("AFD_"+filename[:-4]+"_"+tt+".txt")
