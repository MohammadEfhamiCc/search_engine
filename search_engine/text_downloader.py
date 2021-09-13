# creator: A NOOB programmer
# Episode two of suffering
# MES
from urllib.request import urlopen
from bs4 import BeautifulSoup
from bs4 import UnicodeDammit
import requests
import re
import sys
import textwrap
import textwrap3
import winsound
from colorama import init,Fore
init()
file1 = open('urls_farsi.txt', 'r')
Lines = file1.readlines()
#check_empty = file1.read
rep = 0
rep_new = 0
count = 0
number = set()
file_name_list = list()
if not Lines:
    print()
    #print(emoji.emojize(":/play trombone:"))
    sys.exit("LOL")
for line in Lines:
    count += 1
    print()
    print(Fore.YELLOW+"Line{}: {}".format(count, line.strip()))
    html = urlopen(line).read()
    html = UnicodeDammit.detwingle(html)
    soup = BeautifulSoup(html, features="html.parser")
    for script in soup(["script", "style"]):
        script.extract()    # rip it out
    text = soup.get_text(separator=' ')
    #text = text.replace("“", " ")
    #text = text.replace("“", " ")
    #text = text.replace("”", " ")
    #text = text.replace("”", " ")
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))   
    text = '\n'.join(chunk for chunk in chunks if chunk)
    wrapper = textwrap.TextWrapper(width=78)
    #print("HELLO")
    string_new = wrapper.fill(text=text)
    #string_new = string_new.replace('\\"', '')
    #string_new = string_new.replace("”", " ")
    #string_new = string_new.replace('\\"', '')
    #string_new = string_new.replace("“", " ")
    file_name = "file{}.txt".format(str(rep))
    with open(file_name, 'w', encoding="utf-8") as f:
        #for elements in text:
        print(string_new, file=f)
    f.close
    rep +=1
#     book = open(file_names, encoding="utf-8", errors="xmlcharrefreplace")
#     text_new = book.read()
#     text_new = text_new.replace('\\n', ' ')
#     text_new = text_new.replace('\\ ', '')
#     text_new = text_new.replace('\\', '')
#     book.close
#     file_name_copy = "file_copy{}.txt".format(str(rep_new))
#     file = open(file_name_copy, 'w+')
#     file.writelines(text_new)
#     file.close 
#     rep_new += 1 
#     print(text_new)
    print(Fore.WHITE+text)
    print()
    print(Fore.RED+"##############################################################################")
    print(Fore.RED+"##############################################################################")
    print(Fore.RED+"##############################################################################")
    print(Fore.RED+"##############################################################################")
    print(Fore.RED+"##############################################################################")
    print(Fore.RED+"##############################################################################")
print()
print(Fore.GREEN+"Finished")
duration = 500
freq = 440
winsound.Beep(freq,duration)
#print("Your files are ready for making Index")