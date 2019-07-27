import sqlite3 as sql


def processar(nomeFich):
    fichcmd = open(nomeFich, 'r')
    fichReport = None
    nomeBD = None
    id_atributos = 1
    for line in fichcmd.readlines():
        line = line.strip()  # para apagar \n
        linha = line.split(' ')  # separar por ' ' espaços
        cmd = linha[0]
        if cmd == 'BASE_DADOS':
            nomeBD = linha[1].strip()
        elif cmd == 'CRIAR_TABELAS':
            criar_tabelas(nomeBD)
        elif cmd == 'CARREGAR':
            nomeFich = linha[1].strip()
            carregar_compostos(nomeFich, nomeBD)
        elif cmd == 'REPORT':
            fichReport = linha[1]
        elif cmd == 'LISTA':
            # tenho de voltar a separar, agora por ;
            # LISTA CH3;Alkane -> split(' ') -> [LISTA, CH3;Alkane] -> (pos 1 do array) split(';') -> [CH3, Alkane]
            linha2 = linha[1].split(';')
            # cria lista de formulas empiricas encontradas na BD
            empiricas = findEmpirical(linha2[0], linha2[1], nomeBD)
            # escreve para o ficheiro de acordo com o enunciado
            printtofile(empiricas, fichReport, linha2[0], linha2[1], nomeBD)
      #  elif cmd == 'GRAFICO':
   #         cmd = grafico(nomeFich,atributo,nomeBD)


def printtofile(empiricas, nomeficheiro, empF, atributo, nomeBD):
    f = open(nomeficheiro, 'a')
    #print("LISTA "+empF+" "+atributo+'\n')
    f.write("LISTA "+empF+" "+atributo+'\n')
    bd = sql.connect(nomeBD, isolation_level=None)
    # remove repetidas porque formulas repetidas iam imprimir informacao repetida no ficheiro, as queries a BD ja tratam de encontrar
    # todas as entradas em que dois atributos partilham da mesma formula, como e o caso de
    # Acetic Acid;C2H4O2
    # Methyl Formate;C2H4O2
    empiricas = list(dict.fromkeys(empiricas))
    for formula in empiricas:
        # vai buscar o nome do composto em Compostos cujo atributo seja = atributo e a formula quimica seja = formula
        comando = "SELECT nomeComposto FROM Compostos INNER JOIN Atributos AS A ON A.atributo = '" + atributo + \
            "' AND A.identificadorComposto = Compostos.identificador WHERE formulaQuimica = '" + formula + "';"
        # no caso de *, nao exigo que o nome seja =* porque nao faz sentido, e a procura foi feita em todo o ficheiro
        if (atributo == "*"):
            comando = "SELECT nomeComposto FROM Compostos INNER JOIN Atributos AS A ON A.identificadorComposto = Compostos.identificador WHERE formulaQuimica = '" + formula + "';"
        res = bd.execute(comando)
        row = res.fetchone()
        while row is not None:
            # print('\t'+row[0]+";"+formula+'\n')
            f.write('\t'+row[0]+";"+formula+'\n')
            row = res.fetchone()
    f.close()


def findEmpirical(empF, atrib, nomeBD):
    bd = sql.connect(nomeBD, isolation_level=None)
    com3 = None
    # se o atributo nao for qualquer um, ou seja, diferente de *, tenho de ir buscar as formulas quimicas em Compostos, que obedecem a condicao
    # identificador de composto = identificador de composto na tabela atributos E cujo nome do atributo em Atributos seja igual ao passado pelo comando LISTA no ficheiro orders
    if atrib != "*":
        com3 = "SELECT formulaQuimica FROM Compostos INNER JOIN Atributos AS A ON Compostos.identificador = A.identificadorComposto WHERE A.atributo = '"+atrib+"';"
    else:
        # caso contrario quero todas as formulas quimicas
        com3 = "SELECT formulaQuimica FROM Compostos INNER JOIN Atributos AS A ON Compostos.identificador = A.identificadorComposto;"
    res = bd.execute(com3)
    row = res.fetchone()

    # coloca as formulas encontradas num array
    formulas = []
    while row is not None:
        formulas.append(row[0])
        row = res.fetchone()

    empiricas = []
    # o contaElementos mapeia os elementos da formula e da formula empirica dada no comando LISTA
    # ex: CH -> {"C":1, "H": 1}
    #    C2H6O2 -> {"C":2, "H": 6, "O": 2}
    elementosFormula = {}
    elementosEmpirica = {}
    contaElementos(empF, elementosEmpirica)
    for formula in formulas:
        elementosFormula.clear()
        # agora conta os elementos da formula
        contaElementos(formula, elementosFormula)
        # compara os elementos da empirica com os da formula, se um elemento nao existir ou se o racio entre eles for diferente, da False
        if isEmpirical(elementosEmpirica, elementosFormula):
            empiricas.append(formula)
    bd.close()
    return empiricas


def criar_tabelas(nomeBD):
    bd = sql.connect(nomeBD, isolation_level=None)
    bd.execute('CREATE TABLE IF NOT EXISTS Compostos (identificador INTEGER, nomeComposto TEXT, formulaQuimica TEXT, pontoEbulicao INTEGER, PRIMARY KEY(identificador))')
    bd.execute(
        'CREATE TABLE IF NOT EXISTS Atributos (identificador INTEGER, atributo TEXT, identificadorComposto INTEGER,PRIMARY KEY (identificador))')


def carregar_compostos(nomeFich, nomeBD):
    bd = sql.connect(nomeBD, isolation_level=None)
    # vai buscar o ID maior (ou seja, o mais recente) da tabela Atributos, como o carregamento esta separado em 2 ficheiros
    # e necessario saber em que ID a tabela vai para nao dar erro de unique constraint failed
    id_atributos = bd.execute(
        "SELECT MAX(identificador) AS max_id FROM Atributos;").fetchone()[0]
    # se Atributos nao tiver entradas vai retornar None, logo e preciso inicializar a 1
    if id_atributos == None:
        id_atributos = 1
    else:
        # se encontrar, e preciso incrementar +1 para obter o proximo ID
        id_atributos += 1
    fich = open(nomeFich)
    for linha in fich.readlines():
        linha = linha.split(';')
        identif = linha[0]
        ncomp = linha[1]
        formquim = linha[2]
        ptebul = linha[3]
        atributo = linha[4].strip()
        # insercao na BD
        comCompostos = "INSERT INTO Compostos (identificador, nomeComposto, formulaQuimica, pontoEbulicao) VALUES(" + \
            identif+",'"+ncomp+"','"+formquim+"',"+ptebul+");"
        # aqui preciso de ter cuidado pois as vezes aparece mais do que um atributo. Assim eu separo por virgulas
        # e para cada atributo insiro na tabela Atributos
        atributos = atributo.split(',')
        for atr in atributos:
            comAtributos = "INSERT INTO Atributos (identificador, atributo, identificadorComposto) VALUES(" + \
                str(id_atributos)+",'"+atr+"',"+identif+");"
            id_atributos += 1
        bd.execute(comCompostos)
        bd.execute(comAtributos)
    fich.close()
    bd.close()
    return id_atributos


def contaElementos(formula, dicionario):
    elem = ""
    num = ""
    i = 0
    while i < len(formula):
        # se for letra, e elemento
        if formula[i].isalpha():
            # caso tenha entrado no elif, o elem foi reposto a "", logo len = 0, assim isto trata-se de um elemento novo
            if len(elem) == 0:
                elem = elem + formula[i]
            # mas caso nao tenha entrado no elif, elem nao foi reposto e ainda tenho o mais antigo, sendo assim
            # significa que tenho 2 letras seguidas, o que me diz que o elem anterior (em i-1) so tem 1 atomo
            # ou seja coloco dicionario[elem] = 1, e logo a seguir actualizo o elem para o valor em i
            else:
                dicionario[elem] = 1
                elem = formula[i]
            i = i+1
            # caso o ultimo caractere seja uma letra, significa que esse elemento so tem 1 atomo
            if i == len(formula):
                dicionario[elem] = 1
        elif formula[i].isdigit():
            while i < len(formula) and formula[i].isdigit():
                num = num + formula[i]
                i = i+1
            dicionario[elem] = int(num)
            elem = ""
            num = ""


def isEmpirical(elemE, elemF):
    proportion = 0
    for key in elemF:
        # se o elemento em elemF nao existir em elemE, nao e empirica
        if key not in elemE:
            return False
        else:
            numE = elemE[key]
            numF = elemF[key]
            thisProportion = numE / numF
            # inicializar a proporcao, caso seja a primeira iteracao do for
            if proportion == 0:
                proportion = thisProportion
            # comparar a proporcao actual com a anterior. Se for igual, mantem-se, se for diferente nao e empirica
            if proportion != thisProportion:
                return False
    # se saiu do ciclo e porque nao se verificou nenhuma condicao para nao ser empirica, logo e empirica --> return True
    return True


if __name__ == "__main__":
    processar("orders.txt")
