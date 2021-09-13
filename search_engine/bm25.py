# creator: A NOOB programmer
# Episode four of suffering
# MES
import os
import nltk
from nltk import collections
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import WordPunctTokenizer, word_tokenize
from natsort import natsorted
import codecs
import re
import ast
import getopt
import sys
from math import log10
from operator import itemgetter
from colorama import init, Fore
init()

word_tokenize = word_tokenize
stopwords = set(stopwords.words("english"))
st = nltk.stem.porter.PorterStemmer()
tk = WordPunctTokenizer()

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

class BM25:
    
    def __init__(self,index_file,frequency_file,document_length_file,documents_directory,k, b):
        self.dict_file = codecs.open(index_file, encoding='utf-8')
        self.frequency_temp=codecs.open(frequency_file,encoding='utf-8')
        self.document_length_temp=codecs.open(document_length_file,encoding='utf-8')
        self.documents_directory_temp=documents_directory
        self.dictionary = self.dictionary_fetch()
        self.frequency=self.term_frequency_fetch()
        self.L_ave = 0
        self.N=self.list_documents()
        self.K1 = k
        self.B = b
        self.document_lengths = self.documents_length()
    
    def dictionary_fetch(self):
        dictionary_temp = {}
        for entry in self.dict_file.read().split('\n'):
            if (entry):
                token = entry.split(" ")
                term = token[0]
                document = token[1:]
                document_temp=[int(x) for x in document]
                dictionary_temp[term] = document_temp
        return dictionary_temp

    def term_frequency_fetch(self):
        frequency = {}
        for entry in self.frequency_temp.read().split('\n'):
            if (entry):
                token = entry.split(" ",1)
                term = token[0]
                tf = ast.literal_eval(token[1])
                frequency[term] = tf
        return frequency

    def list_documents(self):
        temp=os.listdir(self.documents_directory_temp)
        size=len(temp)
        return size

    def documents_length(self):
        document_length={}
        file_content=self.document_length_temp.read().split("\n")
        document_length=ast.literal_eval(file_content[0])
        self.L_ave=int(file_content[1])
        return document_length

    def bm25(self,query):
        terms = [st.stem(term) for term in word_tokenize(query) if term.casefold() not in stopwords]
        doc_ids=self.retrieve_document_identifier(query)
        score = {}
        for doc_id in doc_ids:
            score_temp = 0
            for term in terms:
                score_temp += self.compute_idf(term) * self.compute_num(term, doc_id) / self.compute_den(term, doc_id)
            score[doc_id] = score_temp
        sorted_score = sorted(score.items(), key=itemgetter(1), reverse=True)
        print("{} documents found.".format(len(doc_ids)))
        for k, v in sorted_score:
            #print("Document {0} score: {1:.50f}".format(k, v))
            print(Fore.YELLOW+"Document {}".format(k)+Fore.CYAN+" ----------->>> "+Fore.WHITE+"score: {}".format(v))
        print()

    def retrieve_document_identifier(self,query):
        tokens=query.replace(' ',' OR ')
        tokens = tokens.split(' ')
        values_in_stack = []
        postfix_queue = collections.deque(self.PostFix_converter(tokens))
        while postfix_queue:
            token = postfix_queue.popleft()
            result = []
            if (token != 'AND' and token != 'OR' and token != 'NOT'):
                token = st.stem(token)
                if (token in self.dictionary):
                    term = '{}'.format(token)
                    result = self.dictionary[term]
            if (token == 'OR'):
                second_oper = values_in_stack.pop()
                first_oper = values_in_stack.pop()
                result = self.OR_operator(first_oper, second_oper)
            values_in_stack.append(result)
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
        while (operator_stack):
            output.append(operator_stack.pop())
        print(output)
        return output

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

    def compute_idf(self,term):
        df = self.retrieve_document_frequency(term)
        try:
            return log10(self.N / df)
        except ZeroDivisionError:
            return 0
    
    def retrieve_document_frequency(self,term):
        try:
            term_temp='{}'.format(term)
            postings_list = self.dictionary[term_temp]
            return len(postings_list)
        except KeyError:
            return 0

    def compute_num(self, term, doc_id):
        return (self.K1 + 1) * self.retrieve_frequency_of_term_in_doc(term, doc_id)

    def retrieve_frequency_of_term_in_doc(self,term,doc_id):
        try:
            term_temp='{}'.format(term)
            frequency = self.frequency[term_temp][doc_id]
            return frequency
        except KeyError:
            return 0

    def compute_den(self, term, doc_id):
        return self.K1 * ((1 - self.B) + self.B * (self.document_lengths[doc_id] / self.L_ave)) + self.retrieve_frequency_of_term_in_doc(term, doc_id)

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:f:l:d:')
except (getopt.GetoptError, getopt.err):
    sys.exit("Please enter the argument, correctly, try it again.")
for o, a in opts:
    if o == '-i':
        temp_index_file = a
    if o == '-f':
        temp_frequency_file = a
    if o == '-l':
        temp_document_length_file = a
    if o == '-d':
        temp_documents_directory = a

bm25_ranker=BM25(temp_index_file,temp_frequency_file,temp_document_length_file,temp_documents_directory,0.5, 0.5)
#text=Fore.RED+"HELLO"
print(Fore.GREEN+"\nDo you like to use BM25 algorithm,' y ' , means yes, and ' n ', means no:")
termination = input()
#ask_user = input("\nDo you like to use BM25 algorithm, ' y ' , means yes, and ' n ', means no:\n")
#ask_user = input(text)
while termination!='n':
    print(Fore.CYAN+"Please enter you desired query:")
    user_query= input()
    bm25_ranker.bm25(user_query)
    print(Fore.RED+"Do you still want to use BM25 algorithm?")
    termination=input()