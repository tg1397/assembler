ST = []
progloc = 0
OPCODES = ['BRA', 'BEQ', 'BLT', 'BGT', 'ADD', 'SUB', 'MULU', 'DIVU', 'MOVE', 'CMP', 'SWAP', 'DUMP', 'STOP']

def int2hex(num):
    return hex(num)[2:]
    
def hex2int(num):
    return int(num, 16)

def readin():
#    progloc = 0
#    bleh = open(file, 'r')
#    bleh.read().split(' ')

    filename = input("Please input the file you would like assembled. It must be in this same directory: ")
    file = open(filename, 'r')
    everything = file.read()
    return everything, filename 
    
def processin(line):
    """process the input into the LABEL OPCODE OPERAND COMMENT Format"""
    """Can only split objects by tabs or by spaces""" 
    parts = line.split('\t')
    if len(parts) == 1:
        tryagain = line.split(' ')
        if len(tryagain) == 1:
            return 'none'
        elif len(tryagain) == 2:
            return [tryagain[0], tryagain[1], 'none', 'none']
        elif len(tryagain) == 3:
            return [tryagain[0], tryagain[1], tryagain[2], 'none']
        else:
            comment = ''
            for i in range(3, len(tryagain)):
                comment += ' ' + tryagain[i]
            return [tryagain[0], tryagain[1], tryagain[2], comment]
    elif len(parts) == 2:
        return [parts[0], parts[1], 'none', 'none']
    elif len(parts) == 3:
        return [parts[0], parts[1], parts[2], 'none']
    else:
        comment = ''
        for i in range(3, len(parts)):
            comment += ' ' + parts[i]
        return [parts[0], parts[1], parts[2], comment]
    
def pass1(full):
    """full as a list of every line as lists"""
    hasnum = []
    for line in full:
        #breaks up the line
        proc = processin(line)
        if proc != 'none':
            #does the work for pass1, making a new list that includes location
            if proc[1].upper() != 'END':
                individual(proc)
                proc.append(progloc)
            hasnum.append(proc)
    return hasnum
            
def individual(line):
    """Line should be passed as a list in order LABEL, OPCODE, OPERAND, COMMENT"""
    global progloc
    if line[0] != '*':
        if line[0] != '':
            if len(ST) > 0:
                #making symbol table
                for pair in ST:
                    if pair[0] == line[0]:
                        print('error: duplicate symbol')
                ST.append((line[0], progloc))
            else:
                ST.append((line[0], progloc))
        opc = line[1].upper()
        if opc in OPCODES:
            comp = opc[0:3]
            #branching statements
            if opc[0] == 'B':
                progloc += 2
            #all five of these have same operand requirements    
            elif comp == 'CMP' or comp == 'ADD' or comp == 'SUB' or comp == 'MUL' or comp == 'DIV':
                mathcmp(opc, line[2])
            #lots of different moves
            elif comp == 'MOV':
                move(opc, line[2])
            elif opc == 'SWAP':
                if len(line[2]) == 2 and line[2][0] == 'd':
                    progloc += 2
                else:
                    print('error: illegal instruction')
            elif opc == 'STOP' or opc == 'DUMP':
                if line[2] == "#$2700":
                    progloc += 2
                else:
                    print("error: ilegal instruction")
        else:
            if opc == "ORG":
                #accounts for different types of constants
                if line[2][0] == '$':
                    val = hex2int(line[2][1:])
                elif line[2][0] == '#':
                    val = int(line[2][1:])
                else:
                    val = int(line[2])
                progloc = val
            elif opc == "DS":
                progloc += int(line[2]) * 2
            elif opc == "DC":
                num = len(line[2].split(',')) * 2
                progloc += num
            else:
                print("error: illegal opcode")

def move(code, operands):
    """Tests to ensure that the instruction is valid for a MOVE statement
    based on the operands provided"""
    global progloc
    if len(operands) == 5 and (operands[0] == 'd' or operands[0] == 'a') and (operands[3] == 'd' or operands[3] == 'a'):
        progloc += 2
    elif (operands[0] == 'a' or operands[0] == 'd') and '(a' in operands:
        progloc += 4
    elif '(a' in operands and (',a' in operands or ',d' in operands):
        progloc += 4
    else:
        sep = operands.split(',')
        if '(a' in sep[0] and '(a' in sep[1]:
            progloc += 6
        else:
            print("error: illegal instruction")
    

def mathcmp(code, operands):
    """Tests to ensure that the code is a valid instruction for either math
    operations or compare statement"""
    global progloc
    if code == 'ADD':
        #add is the only one that has a chance for an address register here
        both = operands.split(',')
        if len(both) == 2 and both[0][0] == 'd' and (both[1][0] == 'a' or both[1][0] == 'd'):
            progloc += 2
        else:
            print("error: illegal instruction")
    else:
        if len(operands) == 5 and operands[0] == 'd' and operands[3] == 'd':
            progloc += 2
        else:
            print("error: illegal instruction")


def bin2hex(binval):
    norm = int(binval, 2)
    return hex(norm)[2:]

def int2bin(num):
    return bin(num)[2:]

def pass2(orig, full, filename):
    """This is where the file creation happens"""
    obj = ''
    #Leftover object
    loobj = ''
    file = filename[0:-4] + '.hex'
    newfile = open(file, 'w')
    filelst = filename[0:-4] + '.lst'
    lstfile = open(filelst, 'w')
    firstline = "S004000000XX \n"
    newfile.write(firstline)
    obj += "S1"
    #leftover instruction
    leftover = ''
    inst = ''
    for i in range(len(full)):
        line = full[i]
        #proc = processin(line)
        #print(proc)
        #when the obj only has the S1 value, add location
        if len(obj) == 2:
            loc = int2hex(line[4])
            while len(loc) < 4:
                loc = '0' + loc
            obj += loc + loobj
        inst = leftover
        if line != 'none':
            #objmaker returns the binary of the instruction
            if line[1].upper() != 'ORG' and line[1].upper() != 'DS':
                recent = objmaker(line)
                for digit in recent:
                    inst += digit
                fuckit = recent
            else:
                #org and ds create a new line
                long = len(obj) // 2
                if long < 10:
                    long = '0' + str(long)
                else:
                    long = int2hex(long)
                    if len(long) < 2:
                        long = '0' + long
                obj = obj[0:2] + long + obj[2:] + 'XX \n'
                newfile.write(obj.upper())
                obj = "S1"
        #transforms instructions by each byte
        while len(inst) >= 8:
            value = bin2hex(inst[0:8])
            if line[2].upper() == "DC":
                while len(value) < 4:
                    value = '0' + value
            obj += value
            inst = inst[8:]
            #checks to see if line is too long for file
            if len(obj[2:]) // 2 >= 13:
                obj = obj[0:2] + '13' + obj[2:26] + 'XX \n'
                newfile.write(obj.upper())
                obj = "S1"
                leftover = inst
                loobj = obj[26:]
                inst = ''
        #for listfile, checks for comment
        if line[0] != '' and line[0][0] == '*':
                otpt = ' ' * 23 + str(i + 1) + ' ' + orig[i] + '\n'
                lstfile.write(otpt)
        else:
        #otherwise, location etc are necessary
            loc = int2hex(line[4])
            while len(loc) < 8:
                loc = '0' + loc
            otpt = loc + '  '
            if line[2].upper() == "ORG" or line[2].upper() == "DS":
                otpt += ' ' * 12
            else:
                if len(fuckit) > 0:
                    #for whatever reason, this broke everything in the list file
                    #so I settled for having just the binary instructions
                    #fuckit = bin2hex(fuckit)
                    if len(fuckit) > 4:
                        while len(fuckit) % 4 != 0:
                            fuckit += ' '
                        otpt += fuckit[0:4] + ' ' + fuckit[4:] + ' ' + str(i + 1)
                    #makes the instruction a word long
                    elif len(fuckit) < 4:
                        while len(fuckit) < 4:
                            fuckit = '0' + fuckit
                        otpt += fuckit + ' ' * 8 + str(i + 1) + ' '
                else:
                    otpt += ' ' * 14 + str(i + 1) + ' '
                otpt += orig[i] + '\n'
                lstfile.write(otpt)
                fuckit = ''
                    
    #by the end of the file
    if len(leftover) > 0:
        obj += bin2hex(leftover)
    #create one more line before the S9
    if len(obj) > 6:
        if len(obj) % 2 != 0:
            obj += '0'
        long = len(obj) // 2
        if long < 10:
            long = '0' + str(long)
        else:
            long = int2hex(long)
            if len(long) < 2:
                long = '0' + long
        obj = obj[0:2] + long + obj[2:] + 'XX \n'
        newfile.write(obj.upper())
    endline = "S9030000XX"
    newfile.write(endline)
            
def objmaker(line):
    """Based on instruction and instruction type, do the binary codes as strings"""
    inst = ''
    if line[0] != '*':
        opc = line[1].upper()
        ope = line[2]
        opesep = ope.split(',')
        if opc in OPCODES:
            if opc == "ADD":
                inst = "1101"
                num = opesep[1][1]
                inst += reg(num)
                if ope[3] == 'd':
                    inst += "001000"
                else:
                    inst += "011000"
                num = opesep[0][1]
                inst += reg(num)
                return inst
            elif opc == "SUB":
                inst = "1001"
                num = opesep[1][1]
                inst += reg(num)
                inst += "0010000"
                num = opesep[0][1]
                inst += reg(num)
                return inst
            elif opc == "MULU":
                inst = '1100'
                num = opesep[1][1]
                inst += reg(num)
                inst += "111000"
                num = opesep[0][1]
                inst += reg(num)
                return inst
            elif opc == "DIVU":
                inst = '1000'
                num = opesep[1][1]
                inst += reg(num)
                inst += "111000"
                num = opesep[0][1]
                inst += reg(num)
                return inst
            elif opc == "CMP":
                inst = '1011'
                num = opesep[1][1]
                inst += reg(num)
                inst += "001000"
                num = opesep[0][1]
                inst += reg(num)
                return inst
            elif opc == "SWAP":
                inst = "010010000100"
                num = opesep[0][1]
                inst += reg(num)
                return inst
            elif opc == "STOP":
                return "0100111001000000"
            elif opc == "BRA":
                inst = "01100000"
                for pair in ST:
                    if ope == pair[0]:
                        loc = pair[1]
                        return inst + displaceb(line[4], loc)
                print("error: illegal symbol")
            elif opc == "BEQ":
                inst = "01100111"
                for pair in ST:
                    if ope == pair[0]:
                        loc = pair[1]
                        return inst + displaceb(line[4], loc)
                print("error: illegal symbol")
            elif opc == "BGT":
                inst = "01101110"
                for pair in ST:
                    if ope == pair[0]:
                        loc = pair[1]
                        return inst + displaceb(line[4], loc)
                print("error: illegal symbol")
            elif opc == "BLT":
                inst = "01101101"
                for pair in ST:
                    if ope == pair[0]:
                        loc = pair[1]
                        return inst + displaceb(line[4], loc)
                print("error: illegal symbol")
            elif opc == "MOVE":
                inst = "0011"
                if len(opesep[0]) == 2 and len(opesep[1]) == 2:
                    source = reg(opesep[0][1])
                    dest = reg(opesep[1][1])
                    if opesep[0][0] == 'd':
                        if opesep[1][0] == 'd':
                            return inst + dest + "000000" + source
                        else:
                            return inst + dest + "001000" + source
                    else:
                        if opesep[1][0] == 'd':
                            return inst + dest + "000001" + source
                        else:
                            return inst + dest + "001001" + source
                elif len(opesep[0]) == 2 and len(opesep[1]) > 2:
                    source = reg(opesep[0][1])
                    where = opesep[1].index('(')
                    areg = reg(opesep[1][where + 2])
                    const = opesep[1][0:where]
                    if const.isnumeric():
                        const = int2bin(int(const))
                    else:
                        for pair in ST:
                            if pair[0] == const:
                                const = int2bin(pair[1])
                        if not const.isnumeric():
                            print("error: invalid symbol")
                    
                    if opesep[0][0] == 'd':
                        return inst + areg + '101000' + source + const
                    else:
                        return inst + areg + '101001' + source + const
                elif len(opesep[0]) > 2 and len(opesep[1]) == 2:
                    where = opesep[0].index('(')
                    areg = reg(opesep[0][where + 2])
                    dest = reg(opesep[1][1])
                    const = opesep[0][0:where]
                    if const.isnumeric():
                        const = int2bin(int(const))
                    else:
                        for pair in ST:
                            if pair[0] == const:
                                const = int2bin(pair[1])
                        if not const.isnumeric():
                            print("error: invalid symbol")
                    
                    if opesep[1][0] == 'd':
                        return inst + dest + '000101' + areg + const
                    else:
                        return inst + dest + '001101' + areg + const
                else:
                    where1 = opesep[0].index('(')
                    where2 = opesep[1].index('(')
                    areg1 = reg(opesep[0][where1 + 2])
                    areg2 = reg(opesep[1][where2 + 2])
                    sconst = opesep[0][0:where1]
                    dconst = opesep[0][0:where2]
                    if sconst.isnumeric():
                        sconst = int2bin(int(sconst))
                    else:
                        for pair in ST:
                            if pair[0] == sconst:
                                sconst = int2bin(pair[1])
                        if not sconst.isnumeric():
                            print("error: invalid symbol")
                    if dconst.isnumeric():
                        dconst = int2bin(int(dconst))
                    else:
                        for pair in ST:
                            if pair[0] == dconst:
                                dconst = int2bin(pair[1])
                        if not dconst.isnumeric():
                            print("error: invalid symbol")
                    
                    return inst + areg2 + '101101' + areg1 + sconst + dconst
                               
        elif opc == "DC":
            for obj in opesep:
                x = str(obj)
                if x.isnumeric():
                    ind = bin(int(obj))[2:]
                    while len(ind) < 8:
                        ind = '0' + ind
                    inst += ind
                else:
                    for let in obj:
                        asc = ord(let)
                        ind = bin(asc)[2:]
                        while len(ind) < 8:
                            ind = '0' + ind
                        inst += ind
            return inst
    return ''

def displaceb(fro, to):
    """branching displacement"""
    dif = to - fro
    bi = bin(dif)[2:0]
    while len(bi) < 8:
        bi = '0' + bi
    return bi

def reg(num):
    """register binary"""
    if num == "0":
        return "000"
    elif num == "1":
        return "001"
    elif num == "2":
        return "010"
    elif num == "3":
        return "011"


def main():
    """Calls pass 1 and 2"""
    global progloc
    everything, filename = readin()
    full = everything.split('\n')
    newfull = pass1(full)
    pass2(full, newfull, filename)
    

main()
