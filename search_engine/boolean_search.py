# creator: A NOOB programmer
# Episode four of suffering
# MES
import nltk
import sys
import getopt
import codecs
import struct
import math
import io
import nltk
import collections
from natsort import natsorted
from colorama import init, Fore
init()

Post_size = 4
is_query_in_standard_form = True

class bcolors:
    OK = '\033[92m' #GREEN
    WARNING = '\033[93m' #YELLOW
    FAIL = '\033[91m' #RED
    RESET = '\033[0m' #RESET COLOR

class SEARCH:

    def __init__(self,dictionary_file, postings_file, queries_file, output_file):
        self.dict_file = codecs.open(dictionary_file, encoding='utf-8')
        self.post_file = io.open(postings_file, 'rb')
        self.query_file = codecs.open(queries_file, encoding='utf-8')
        self.out_file = open(output_file, 'w')
        self.loaded_dict = self.dictionary_fetch()
        self.dictionary = self.loaded_dict[0]
        self.indexed_docIDs = self.loaded_dict[1]
        self.dict_file.close()

    def document_retrieval(self):
        queries_list = self.query_file.read().splitlines()
        y = 0
        for x in range(len(queries_list)):
            query = queries_list[x]
            result = self.compile_query(query)
            self.out_file.write("({}th) answer of query, is -------->> ".format(y))
            for j in range(len(result)):
                docID = str(result[j])
                if (j != len(result) - 1):
                    docID += ', '
                self.out_file.write(docID)
            if (x != len(queries_list) - 1):
                self.out_file.write('\n')
            if (len(queries_list)>1):
                print(Fore.CYAN+"################################################")
                print(Fore.CYAN+"################################################")
                print(Fore.CYAN+"################################################")
                print(Fore.CYAN+"################################################")
                print(Fore.CYAN+"################################################")
                print(Fore.CYAN+"################################################")
            y+=1
        self.post_file.close()
        self.query_file.close()
        self.out_file.close()

    def dictionary_fetch(self):
        dictionary = {}
        indexed_docIDs = []
        docIDs_processed = False
        for entry in self.dict_file.read().split('\n'):
            if (entry):
                if (not docIDs_processed):
                    count = 0
                    indexed_docIDs_total = [docID for docID in entry[19:-1].split(',')]
                    indexed_docIDs_total = natsorted(indexed_docIDs_total)
                    for x in range(len(indexed_docIDs_total)):
                        indexed_docIDs.append(count)
                        count += 1
                    docIDs_processed = True
                    print(Fore.GREEN+ "\nthe documents that have been indexed in order are:\n")
                    for x in indexed_docIDs_total:
                        print(Fore.YELLOW + x)
                else:
                    token = entry.split(" ")
                    term = token[0]
                    df = int(token[1])
                    offset = int(token[2])
                    dictionary[term] = (df, offset)
        return (dictionary, indexed_docIDs)

    @staticmethod
    def posting_list_fetch(post_file,length, offset):
        post_file.seek(offset)
        posting_list = []
        for i in range(length):
            posting = post_file.read(Post_size)
            docID = struct.unpack('I', posting)[0]
            posting_list.append(docID)
        return posting_list

    def compile_query(self, query):
        st = nltk.stem.porter.PorterStemmer()
        query = query.replace(')', ' )')
        query = query.replace('(', '( ')
        values_in_stack = []
        query = query.split(' ')
        postfix_queue = collections.deque(self.PostFix_converter(query))
        while postfix_queue:
            token = postfix_queue.popleft()
            result = []
            if (token != 'AND' and token != 'OR' and token != 'NOT'):
                token = st.stem(token)
                if (token in self.dictionary):
                    print("#####################################################################")
                    result = self.posting_list_fetch(self.post_file, self.dictionary[token][0], self.dictionary[token][1])
                    print(Fore.YELLOW+"Push the token into the stack:", Fore.GREEN+"{}".format(token))
                    print(Fore.RED+"{}".format(result))
                    print(Fore.YELLOW+"the current status of deque is:",Fore.GREEN+"{}".format(postfix_queue))
                    print("#####################################################################")
                    print("\n")
            if (token == 'AND'):
                print("#####################################################################")
                second_oper = values_in_stack.pop()
                first_oper = values_in_stack.pop()
                result = self.AND_operator(first_oper, second_oper)
                print(Fore.YELLOW+"the 'AND' between two token:",Fore.GREEN+"{}, and {}".format(second_oper,first_oper))
                print(Fore.RED+"{}".format(result))
                print(Fore.YELLOW+"the current status of deque is:",Fore.GREEN+"{}".format(postfix_queue))
                print("#####################################################################")
                print("\n")
            if (token == 'OR'):
                print("#####################################################################")
                second_oper = values_in_stack.pop()
                first_oper = values_in_stack.pop()
                result = self.OR_operator(first_oper, second_oper)
                print("the 'OR' between two token: {} and {}".format(second_oper,first_oper))
                print(Fore.RED+"{}".format(result))
                print(Fore.YELLOW+"the current status of deque is:",Fore.GREEN+"{}".format(postfix_queue))
                print("#####################################################################")
                print("\n")
            if (token == 'NOT'):
                print("#####################################################################")
                second_oper = values_in_stack.pop()
                result = self.Not_operator(second_oper, self.indexed_docIDs)
                print("the 'NOT' of token: {}".format(second_oper))
                print(Fore.RED+"{}".format(result))
                print(Fore.YELLOW+"the current status of deque is:",Fore.GREEN+"{}".format(postfix_queue))
                print("#####################################################################")
                print("\n")
            values_in_stack.append(result)
            print("the values in final stack:",values_in_stack)                       
        if len(values_in_stack) != 1:
            print (Fore.LIGHTMAGENTA_EX+"error, Please, enter the correct query")
            #values_in_stack="error"
        return values_in_stack.pop()

    @staticmethod
    def PostFix_converter(query):
        output = []
        operator_stack = []     
        priority_value = {"NOT":4,"AND":3,"OR":2,"(":1,")":1}    
        
        for token in query:
            if (token == '('):
                operator_stack.append(token)
            elif (token == ')'):
                operator = operator_stack.pop()
                while operator != '(':
                    output.append(operator)
                    operator = operator_stack.pop()
            elif (token in priority_value):
                if (operator_stack):
                    top_of_stack_operator = operator_stack[-1]
                    while (operator_stack and priority_value[top_of_stack_operator] > priority_value[token]):
                        output.append(operator_stack.pop())
                        if (operator_stack):
                            top_of_stack_operator = operator_stack[-1]
                operator_stack.append(token)
            else:
                output.append(token.lower())

        t = True
        while (operator_stack):
            output.append(operator_stack.pop())
            if t:
                print("\nplease the next time, use more readable query than this time, i mean use more '(' and ')' for your own ease\n")
                t = False
        print(Fore.GREEN+"the infix query is:\n",Fore.CYAN+"{}".format(query))
        print(Fore.GREEN+"the postfix query is:\n",Fore.CYAN+"{}".format(output))
        print("\n")
        return output

    @staticmethod
    def Not_operator(second_oper, indexed_docIDs):
        if (not second_oper):
            return indexed_docIDs
        result = []
        second_position = 0
        for item in indexed_docIDs:
            if (item != second_oper[second_position]):
                result.append(item)
            elif (second_position + 1 < len(second_oper)):
                second_position += 1
        return result

    @staticmethod
    def OR_operator(first_oper, second_oper):
        result = []
        first_position = 0
        second_position = 0
        while (first_position < len(first_oper) or second_position < len(second_oper)):
            if (first_position < len(first_oper) and second_position < len(second_oper)):
                first_value = first_oper[first_position]
                second_value = second_oper[second_position]
                if (first_value == second_value):
                    result.append(first_value)
                    first_position += 1
                    second_position += 1
                elif (first_value > second_value):
                    result.append(second_value)
                    second_position += 1
                else:
                    result.append(first_value)
                    first_position += 1
            elif (first_position >= len(first_oper)):
                second_value = second_oper[second_position]
                result.append(second_value)
                second_position += 1
            else:
                first_value = first_oper[first_position]
                result.append(first_value)
                first_position += 1
        return result

    @staticmethod
    def AND_operator(first_oper, second_oper):
        result = []
        first_position = 0
        second_position = 0
        first_jump = int(math.sqrt(len(first_oper)))
        second_jump = int(math.sqrt(len(second_oper)))
        while (first_position < len(first_oper) and second_position < len(second_oper)):
            first_value = first_oper[first_position]
            second_value = second_oper[second_position]
            if (first_value == second_value):
                result.append(first_value)
                first_position += 1
                second_position += 1
            elif (first_value > second_value):
                if (second_position + second_jump < len(second_oper)) and second_oper[second_position + second_jump] <= first_value:
                    second_position += second_jump
                else:
                    second_position += 1
            else:
                if (first_position + first_jump < len(first_oper)) and first_oper[first_position + first_jump] <= second_value:
                    first_position += first_jump
                else:
                    first_position += 1
        return result

dictionary_file = postings_file = queries_file = output_file = None
try:
    arguments, temp = getopt.getopt(sys.argv[1:], 'd:p:q:r:')
except (getopt.GetoptError, getopt.err):
    sys.exit("Please, enter the four argument correctly, try again!!!!!!!!!!!!!")
for o, a in arguments:
    if o == '-d':
        dictionary_file = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        queries_file = a
    elif o == '-r':
        output_file = a

if (dictionary_file == None or postings_file == None or queries_file == None or output_file == None):
    sys.exit(Fore.RED+"\nPlease check your argument")
search_init = SEARCH(dictionary_file, postings_file, queries_file, output_file)
search_start = search_init.document_retrieval()
print(Fore.GREEN + "\nFINISH")