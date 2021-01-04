import subprocess
import os
import sys

def lengthCheck(number_byte_message):
    ''' (integer) -> bool '''
    number_byte_storage = 2000 * 8
    if number_byte_message > number_byte_storage:
        return True
    return False


def getListRep(dir_path):
    ''' (string) -> array<string> '''
    list_rep=[]
    for i in os.listdir(dir_path):
        try :
            if (int(i) >= 0 and int(i) < 10000):
                if os.path.isdir(dir_path + "/" + i):
                    list_rep.append(i)
        except ValueError:
            continue
    return list_rep

def createRepertory(dir_path):
    ''' (string) -> string '''
    # try create repertory
    try:
        os.makedirs(dir_path)
    except OSError:
        if not os.path.isdir(dir_path):
            Raise

    list_rep = getListRep(dir_path)
    
    #if there are directories, if not, we create directory 0000
    if(len(list_rep) > 0):
        name_repertory = int(list_rep[len(list_rep)-1])
        name_repertory += 1
        new_repertory = str(name_repertory).zfill(4)
    else:
        new_repertory = "0000"
    new_path_repertory = dir_path + '/' + new_repertory
    os.makedirs(new_path_repertory)
    return new_path_repertory


def generateNumber(number_bytes):
    ''' (integer) -> binary '''
    with open("/dev/urandom", 'rb') as f:
        tmp = f.read(number_bytes)
        number = ''
        for i in range(number_bytes):
            number += (bin(tmp[i])[2:].zfill(8))
    return number

def writeFile(path_File, content):
    ''' (string, integer) -> none '''
    f = open(path_File, "w")
    f.write(str(content))
    f.close()

def generate(dir_path):
    ''' (string) -> none '''
    new_path_repertory = createRepertory(dir_path)
    for i in range(0, 100):
        path_File = new_path_repertory + '/' + str(i).zfill(2)
        writeFile(path_File + 'p', generateNumber(48))
        writeFile(path_File + 's', generateNumber(48))
        writeFile(path_File + 'c', generateNumber(2000))
    print("Generate finish")

def splitBinary(content):
    '''(binary) -> array<binary> '''
    split_pad = []
    for i in range (0, len(content), 8):
        split_pad.append(content[i : i + 8])
    return split_pad

def binToChar(path_repertory_current, type_file):
    '''(string, char) -> string '''
    f = open(path_repertory_current + type_file, "r")
    list_pad = splitBinary(f.readlines()[0])
    new_char = ""
    for index_message in range(len(list_pad)):
        # Use the mask on each character
        new_char += chr(int(list_pad[index_message], 2))
    f.close()
    return new_char

def checkBinary(byte_list, binary_verif):
    '''(array<binary>, string) -> bool '''
    split_pad = splitBinary(binary_verif)
    if byte_list == split_pad :
        return True
    return False

def cleanBinary(byte_list):
    '''(array<binary>) -> (array<binary>, array<binary>, array<binary>) '''
    return (byte_list[0 : 48]), (byte_list[48 : len(byte_list)-48]), (byte_list[len(byte_list)-48 : len(byte_list)])

def writeFile(name, message):
    '''(string, string) -> none '''
    f = open(name , "w")
    f.write(message)
    f.close()

def send(dir_path, message):
    '''(string, string) -> none '''
    number_byte_message = len(message) * 8 
    if(lengthCheck(number_byte_message)):
        sys.exit('Error length message. Stop program')
    if not(os.path.isdir(dir_path)):
         sys.exit('Directory does not exist. Stop program')

    list_rep = getListRep(dir_path)
    if (len(list_rep) < 1):
        sys.exit('No existing PAD. Stop program')

    find = False
    for rep in range(len(list_rep)):
        new_path_repertory = dir_path + '/' + list_rep[rep]
        for i in range(0, 100):
            path_file = new_path_repertory + '/' + str(i).zfill(2) + 'c'
            if(os.path.exists(path_file)):
                path_pad = path_file
                path_repertory_current = new_path_repertory + '/' + str(i).zfill(2)
                #if the file does not comply, we go to the next one
                try:
                    suffix = binToChar(path_repertory_current, "p")
                    f = open(path_pad, "r")
                    msg = ""
                    list_pad = splitBinary(f.read())
                    for index_message in range(len(message)):
                        # Use the mask on each character and XOR operator
                        msg += chr(ord(message[index_message]) ^ int(list_pad[index_message], 2))
                    f.close()
                    prefix = binToChar(path_repertory_current, "s")
                    #replaced to construct the file name
                    path_message = path_repertory_current.replace('/', '-') + 't'
                    writeFile(path_message, suffix + msg + prefix)
                    #shred file p
                    subprocess.Popen(['shred', path_pad])
                    find = True
                    break
                except:
                    continue
        if(find):
            break
    if not(find):
        sys.exit('No existing PAD. Stop program')


def receive(dir_path, filename):
    '''(string, string) -> none '''
    if not(os.path.isdir(dir_path)):
         sys.exit('Directory does not exist. Stop program')
    if not(os.path.exists(filename)):
        sys.exit('File does not exist. Stop program')

    list_rep = getListRep(dir_path)
    if (len(list_rep) < 1):
        sys.exit('No existing PAD. Stop program')

    try:
        f = open(filename, "r")
        msg_chiffre = f.read()
        byte_list = []
        for i in range(len(msg_chiffre)):
            binary_representation = bin(ord(msg_chiffre[i]))
            byte_list.append(binary_representation[2:].zfill(8))
            
        f.close()
        suffix_msg, binary_msg, prefix_msg = cleanBinary(byte_list)
    except:
        sys.exit('File error. Stop program')

    find = False
    for rep in range(len(list_rep)):
        new_path_repertory = dir_path + '/' + list_rep[rep]
        for i in range(0, 100):
            path_file = new_path_repertory + '/' + str(i).zfill(2) + 'p'
            # try , if error continue
            try:
                if(os.path.exists(path_file)):
                    # load suffix
                    f = open(path_file, "r")
                    suffix = f.read()
                    f.close()
                    if (checkBinary(suffix_msg, suffix)):
                        path_pad = path_file[:-1] + 'c'
                        f = open(path_pad, "r")
                        list_pad = splitBinary(f.read())
                        msg = ""
                        for index_message in range(len(binary_msg)):
                            # Use the mask on each character and XOR operator
                            msg += chr(int(binary_msg[index_message], 2) ^ int(list_pad[index_message], 2))
                        f.close()
                        find = True
                        path_message = path_file.replace('/', '-')[:-1] + 'm'
                        writeFile(path_message, msg)
                        #shred file p
                        subprocess.Popen(['shred', path_pad])
                        subprocess.Popen(['shred', filename])
                        break
            except:
                continue
        if(find):
            break
    if not (find):
        sys.exit('No existing PAD. Stop program')
