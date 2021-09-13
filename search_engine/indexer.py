# creator: A NOOB programmer
# Episode three of suffering
# MES
import os
import nltk
from nltk import collections
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import WordPunctTokenizer, word_tokenize
import time
import struct
from nltk.util import guess_encoding, pr
import re
from natsort import natsorted
import codecs
from colorama import init,Fore
import re
import ast
import json

init()

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(os.path.realpath(THIS_DIR))

word_tokenize = word_tokenize
stopwords = set(stopwords.words("english"))
ps = nltk.stem.porter.PorterStemmer()
tk = WordPunctTokenizer()
BYTE_SIZE = 4

class BOOLEAN_FORAMT:

    @staticmethod
    def sorting_index():
        #index_address = "C:\\Users\\MES\\Desktop\\prozhe_copy1\\SPIMI\\SPIMI_1\\results\\index.txt"
        index_address = "/".join([ROOT_DIR, "results\index.txt"])
        index_address_sorted = "/".join([ROOT_DIR, "results\index_sorted.txt"])
        f1 = codecs.open(index_address, 'r', encoding='utf-8')
        g1 = codecs.open(index_address_sorted, "w", encoding='utf-8')
        lines_index = f1.readlines()[1:]
        #lines_index = f1.readlines()
        for lines in lines_index:
            elements = lines.split(" ")
            term_current = elements[0]
            postings_current = elements[1:]
            postings_current_sorted = list()
            for x in postings_current:
                postings_current_sorted.append(int(x))
            postings_current_sorted = natsorted(postings_current_sorted)
            #postings_current_sorted = sorted(postings_current)
            g1.write(term_current + " " + str([document_id for document_id in postings_current_sorted])[1:-1].replace(",", "") + "\n")
        f1.close
        g1.close

    @staticmethod
    def final_part(files_list_sorted):
        index_address = "/".join([ROOT_DIR, "results\index.txt"])
        index_address_sorted = "/".join([ROOT_DIR, "results\index_sorted.txt"])
        dictionary_file = "/".join([ROOT_DIR, "results\dictionary.txt"])
        postings_file = "/".join([ROOT_DIR, "results\postings.txt"])
        dics_file = codecs.open(dictionary_file, 'w', encoding='utf-8')
        post_file = open(postings_file, 'wb')
        index_reading = codecs.open(index_address_sorted, encoding='utf-8')
        byte_offset = 0
        total_number_of_terms = 0
        docs_indexed = len(files_list_sorted)
        dics_file.write('Indexed from docIDs:')
        for x in range(docs_indexed):
            dics_file.write(str(files_list_sorted[x]) + ',')
        dics_file.write('\n')
        for entry in index_reading.read().split('\n'):
            if entry != '':
                token = entry.split(" ")
                term = token[0]
                positngs_number = token[1:]
                df = len(positngs_number)
                for docID in positngs_number:
                    posting = struct.pack('I', int(docID))
                    post_file.write(posting)
                dics_file.write(term + " " + str(df) + " " + str(byte_offset)+ "\n")
                byte_offset += BYTE_SIZE * df
                total_number_of_terms += 1       
        print(Fore.YELLOW+"Total number of terms in the index file is:", Fore.GREEN+"{}".format(total_number_of_terms))
        dics_file.close()
        post_file.close()

class Documents:

    def __init__(self, number_of_files, docs_per_block,remove_stopwords, stem, case_folding, remove_numbers):
        self.files_directory = "/".join([ROOT_DIR, "data"])
        self.files_list = self.init_files_list()[:number_of_files]
        self.docs_per_block = docs_per_block
        self.number_of_documents = 0
        self.number_of_tokens = 0
        self.remove_stopwords = remove_stopwords
        self.stem = stem
        self.case_folding = case_folding
        self.remove_numbers = remove_numbers
        self.will_compress = self.remove_stopwords or self.stem or self.case_folding or self.remove_numbers
        self.list_of_lists_of_tokens = []
        self.document_lengths = {}
        self.average_document_length = 0
        self.number_of_blocks=0
        self.documents_length_dir="C:\\Users\\MES\\Desktop\\implementation\\phase3\\eng\\results\\document_length.txt"

    def init_files_list(self):
        files_list = [os.path.join(self.files_directory, file)
                         for file in os.listdir(self.files_directory)]                 
        return natsorted(files_list)

    def get_tokens(self):
        tokens = []
        current_document = 0
        print("Start parsing...\n")
        document_id = 0
        for file in self.files_list:
            file_whole = codecs.open(file, encoding='utf-8')
            document_whole = file_whole.read()
            #terms = tk.tokenize(document_whole)
            terms_total = tk.tokenize(document_whole)
            #terms = word_tokenize(document_whole)
            terms = list()

            for term in terms_total:
                #if re.search("([a-zA-Z])\w+", term): # \w=[a-zA-Z0_9]
                if re.search("\w{2}", term): # \w=[a-zA-Z0_9]
                    terms.append(term)

            if self.will_compress:
                terms = self.compress(terms)
            token_pairs = [(term, document_id) for term in terms]
            tokens.extend(token_pairs)
            self.number_of_documents += 1
            self.document_lengths[document_id] = len(token_pairs)
            current_document += 1
            if current_document == self.docs_per_block:
                self.number_of_tokens += len(tokens)
                self.list_of_lists_of_tokens.append(tokens)
                tokens = []
                current_document = 0
            document_id += 1
        if tokens:
            self.number_of_tokens += len(tokens)
            self.list_of_lists_of_tokens.append(tokens)

        self.average_document_length = self.number_of_tokens / self.number_of_documents

        print(Fore.YELLOW+"Number of available Documents:", Fore.GREEN+"{:,}\n".format(self.number_of_documents))
        print(Fore.YELLOW+"Number of tokens that has been seen:", Fore.GREEN+"{:,}\n".format(self.number_of_tokens))
        print(Fore.YELLOW+"Number of Block files:", Fore.GREEN+"{}\n".format(len(self.list_of_lists_of_tokens)))
        self.number_of_blocks=len(self.list_of_lists_of_tokens)
        doc_len=codecs.open(self.documents_length_dir,'w',encoding='utf-8')
        doc_len.write(str(self.document_lengths))
        doc_len.write("\n")
        doc_len.write(str(int(self.average_document_length)))
        #print("Number of available Documents : %s\nNumber of tokens that has been seen : %s\nNumber of block files : %d"
        #      % ("{:,}".format(self.number_of_documents), "{:,}".format(self.number_of_tokens), len(self.list_of_lists_of_tokens)))      
        return self.list_of_lists_of_tokens


    def compress(self, terms):
        if self.remove_numbers:
            terms = [term for term in terms if not term.replace(",", "").replace(".", "").isdigit()]
        if self.stem:
            terms = [ps.stem(term) for term in terms]
        if self.remove_stopwords:
            terms = [term for term in terms if term.lower() not in stopwords]
        if self.case_folding:
            terms = [term.casefold() for term in terms]
        return terms



class SPIMI:

    def __init__(self, documents):
        self.documents = documents

        self.output_directory = "results"
        self.output_directory = "/".join([ROOT_DIR, self.output_directory])

        self.block_prefix = "BLOCK"
        self.block_prefix_frequency = "FREQUENCY_BLOCK"
        self.block_prefix_frequency_count = "FREQUENCY_BLOCK"
        self.block_number = 0
        self.block_suffix = ".txt"
        

        self.output_index = "index"
        self.output_index = "/".join([self.output_directory, self.output_index + self.block_suffix])
        self.frequency_output_index= "index"
        self.frequency_output_index = "/".join([self.output_directory, self.frequency_output_index + self.block_suffix])
        self.frequency_block_file_final="C:\\Users\\MES\\Desktop\\implementation\\phase3\\eng\\results\\frequency.txt"
        self.mkdir_output_directory(self.output_directory)

        self.list_of_lists_of_tokens = self.documents.get_tokens()

    @staticmethod
    def mkdir_output_directory(output_directory):
        try:
            os.mkdir(output_directory)
        except FileExistsError:
            for file in os.listdir(output_directory):
                os.unlink(os.path.join(output_directory, file))

    @staticmethod
    def update_dictionary(dictionary, term):
        dictionary[term] = []
        return dictionary[term]

    @staticmethod
    def fetch_postings_list(dictionary, term):
        return dictionary[term]

    @staticmethod
    def update_postings_list(postings_list, document_id):
        postings_list.append(document_id)

    @staticmethod
    def terms_in_order(dictionary):
        return [term for term in sorted(dictionary)]

    @staticmethod
    def write_block(sorted_terms, dictionary, block_file, frequency_block_file, sorted_documents_in_each_block):

        #temp1=frequency_block_file
        #temp2=documents.number_of_documents
        temp2=sorted_documents_in_each_block
        temp3=[]
        file= codecs.open(block_file, 'w', encoding='utf-8')
        file_frequency= codecs.open(frequency_block_file, 'w', encoding='utf-8')
        #frequency_of_term=list()
        frequency_of_term={}
        #temp_final=dict()
        for term in sorted_terms:
            term_doc_id_res = list()
            temp3=dictionary[term]

            for r in temp2:
                #temp_doc='doc[{}]='.format(r)
                temp_doc=r
                temp_freq=int(temp3.count(r))
                #temp_final=temp_doc+str(temp_freq)
                if temp_freq!=0:
                    frequency_of_term[temp_doc]=temp_freq


            for x in dictionary[term]:
                if x not in term_doc_id_res:
                    term_doc_id_res.append(x)

            term_doc_id = sorted(term_doc_id_res, key=int)

            #for key, value in frequency_of_term.items(): 
                #line_frequency = "%s %s\n" % (term, ' '.join([str(document_frequency) for document_frequency in frequency_of_term]))
            #for key, value in frequency_of_term.items(): 
            #    file_frequency.write('%s:%s\n' % (key, value))
            line_frequency = "%s %s\n" % (term,str(frequency_of_term))
            #line_frequency_temp=line_frequency.replace(":"," ",1)
            file_frequency.write(line_frequency)

            line = "%s %s\n" % (term, ' '.join([str(document_id) for document_id in term_doc_id]))
            file.write(line)
            frequency_of_term={}

        return block_file,frequency_block_file

    def construct_index(self):
        if os.path.exists(self.output_index):
            return self.compute_index()
        block_files = []
        frequency_block_files=[]

        documents_in_each_block=[]

        for list_of_tokens in self.list_of_lists_of_tokens:
            dictionary = {}
            for token in list_of_tokens:

                if token[1] not in documents_in_each_block:
                    documents_in_each_block.append(token[1])
                if token[0] not in dictionary:
                    postings_list = self.update_dictionary(dictionary, token[0])
                if token[0] in dictionary:
                    postings_list = self.fetch_postings_list(dictionary, token[0])

                self.update_postings_list(postings_list, token[1])

            sorted_documents_in_each_block=[]
            sorted_documents_in_each_block=natsorted(documents_in_each_block)
            documents_in_each_block=[]

            self.block_number += 1
            terms = self.terms_in_order(dictionary)

            block_file = "/".join([self.output_directory, "".join([self.block_prefix, str(self.block_number), self.block_suffix])])
            frequency_block_file = "/".join([self.output_directory, "".join([self.block_prefix_frequency, str(self.block_number), self.block_suffix])])

            block_files.append(self.write_block(terms, dictionary, block_file, frequency_block_file, sorted_documents_in_each_block)[0])
            frequency_block_files.append(self.write_block(terms, dictionary, block_file, frequency_block_file, sorted_documents_in_each_block)[1])


        self.merge_frequency_blocks()
        return self.final_block(block_files)

    def final_block(self, block_files):
        block_files = [codecs.open(block_file, encoding='utf-8') for block_file in block_files]
        lines = [block_file.readline()[:-1] for block_file in block_files]
        most_recent_term = ""
        index = 0
        for block_file in block_files:
            if lines[index] == "":
                block_file.pop(index)
                lines.pop(index)
            else:
                index += 1
        with codecs.open(self.output_index, "w", encoding='utf-8') as output_index:
            while len(block_files) > 0:
                min_index = lines.index(min(lines))
                line = lines[min_index]
                current_term = line.split()[0]

                #current_postings = " ".join(map(str, sorted(list(map(int, line.split()[1:])))))
                current_postings = " ".join(map(str, natsorted(list(map(int, line.split()[1:])))))

                if current_term != most_recent_term:
                    output_index.write("\n%s %s" % (current_term, current_postings))
                    most_recent_term = current_term
                else:
                    output_index.write(" %s" % current_postings)
                lines[min_index] = block_files[min_index].readline()[:-1]
                if lines[min_index] == "":
                    block_files[min_index].close()
                    block_files.pop(min_index)
                    lines.pop(min_index)
            output_index.close()
        return self.compute_index()

    def merge_frequency_blocks(self):
        counts=documents.number_of_blocks
        frequency_dict=dict()
        documents_frequencies={}
        for c in range(counts):
            index_address = "/".join([ROOT_DIR, "results\FREQUENCY_BLOCK{}.txt".format(c+1)])
            file_temp=codecs.open(index_address,'r',encoding='utf-8')
            for entry in file_temp.readlines():
                #test_test=entry[0]
                tokens=entry.split(" ",1)
                term=tokens[0]
                documents_frequencies=ast.literal_eval(tokens[1])
                term_temp='{}'.format(term)
                if term_temp in frequency_dict:
                    frequency_dict[term_temp].update(documents_frequencies)
                else:
                    frequency_dict[term_temp]=documents_frequencies
        sorted_dict=collections.OrderedDict(natsorted(frequency_dict.items()))
        print_file=codecs.open(self.frequency_block_file_final, "w", encoding='utf-8')

        #for key,values in sorted_dict.items():
        for key in sorted_dict.keys():
        #print_file.write('%s:%s\n' % (key, values))
            print_file.write(str(key)+' '+str(sorted_dict[key]))
            print_file.write("\n")

    def compute_index(self):
        inverted_index = {}
        index_file = codecs.open(self.output_index, encoding='utf-8')
        index_file.readline()
        for line in index_file:
            line = line.split()
            #inverted_index[line[0]] = sorted(map(int, (line[1:])))
            inverted_index[line[0]] = natsorted(map(int, (line[1:])))
        return inverted_index

    # def compute_index_frequency(self):
    #     inverted_index = {}
    #     index_file = codecs.open(self.frequency_block_file_final, encoding='utf-8')
    #     index_file.readline()
    #     for line in index_file:
    #         line = line.split()
    #         #inverted_index[line[0]] = sorted(map(int, (line[1:])))
    #         inverted_index[line[0]] = natsorted(map(int, (line[1:])))
    #     return inverted_index


docs=2
files_directory = "/".join([ROOT_DIR, "data"])
files_list = [file for file in os.listdir(files_directory)]
files_list_sorted = natsorted(files_list)
number_of_files = len(files_list)
documents = Documents(number_of_files,docs,remove_stopwords=True,stem=False,case_folding=True,remove_numbers=True)
spimi = SPIMI(documents=documents)
index = spimi.construct_index()
#time.sleep(5)
sorted = BOOLEAN_FORAMT.sorting_index()
#time.sleep(5)
final_part = BOOLEAN_FORAMT.final_part(files_list_sorted)