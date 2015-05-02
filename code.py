import neo4j
import pylab
import blessings
import sys
import multiprocessing
import nltk
import nltk.corpus
import pprint
import re
import json
import ast
import os
import copy
import random

from modules import *

reload(sys)
sys.setdefaultencoding('utf-8')

def getlevelDefinition(domain):
    s = 'MATCH (d:`Domain`) WHERE d.OldTerminology = "' +domain+'" RETURN d.levelDefinition'
    x = cursor.execute(s)
    return next(x)[0]

def colour(string,domain):
    
    if domain=="KNOWLEDGE":       return t.red_on_white(string)
    elif domain=="COMPREHENSION": return t.yellow_on_white(string)
    elif domain=="APPLICATION":   return t.cyan_on_white(string)
    elif domain=="ANALYSIS":      return t.green_on_white(string)
    elif domain=="SYNTHESIS":     return t.magenta_on_white(string)
    elif domain=="EVALUATION":    return t.blue_on_white(string)
    '''
    if domain=="KNOWLEDGE":       return t.white_on_red(string)
    elif domain=="COMPREHENSION": return t.white_on_yellow(string)
    elif domain=="APPLICATION":   return t.white_on_cyan(string)
    elif domain=="ANALYSIS":      return t.white_on_green(string)
    elif domain=="SYNTHESIS":     return t.white_on_magenta(string)
    elif domain=="EVALUATION":    return t.white_on_blue(string)
    '''

def accumulate(domain):
    levels[domain]+=1
    

def draw():        
    colors= ['red','yellow','cyan', 'green', 'violet','blue']
    pylab.figure(1, figsize=(10,10))
    ax = pylab.axes([0.1, 0.1, 0.8, 0.8])
    fracs = []
    for i in domainNames:
        try:
            frac = (levels[i]*100)/total_levels
            fracs.append(frac)
        except:
            print "All values Null"
            return
        
    explode=[0.05 if i==max(fracs) else 0 for i in fracs]
    pylab.pie(fracs, explode=explode, colors = colors , labels=domainNames, autopct='%1.1f%%', shadow=True, startangle=90)
    pylab.title("Blooms Taxonomy", bbox={'facecolor':'0.8', 'pad':5})
    pylab.show()


def check_in_dict(x):
    s = ""
    for i in domainNames:
        if x.title() in domain[i]:
            s+=i+"@"
            
    return s

def check_for_synonyms(j):
    s =  ''
    synos = nltk.corpus.wordnet.synsets(j)
    for i in synos:
        lemma = str(i)[8:-7]
        #print lemma
        s_lemma = check_in_dict(lemma)
        #print s_lemma
        if '@' in s_lemma:
            s+=s_lemma
            #print s
            return s
    return s
    
    
def dump_json(qno,mo,mm,ds):
    with open('loads.json','a') as f:     
        f.write(json.dumps("{'question_number':'"+qno+"','marks_obtained':"+str(mo)+",'maximum_marks':"+str(mm)+",'domains':"+repr(ds)+"}")+'\n')
        

def read_json_by_question(q):
    with open('loads.json') as f: 
        dumps = [ast.literal_eval(json.loads(i.strip())) for i in f]
        return [i for i in dumps if i['question_number'] == q]


def read_json_by_domains(q):
    with open('loads.json') as f: 
        dumps = [ast.literal_eval(json.loads(i.strip())) for i in f]
        return [i for i in dumps if q in i['domains']]
        

def bolden(s):  
    return "\033[1m {} \033[0;0m".format(s)

def under(s):  
    return "\033[4m {} \033[0;0m".format(s)
    

domainNames = [ "KNOWLEDGE" , "COMPREHENSION" , "APPLICATION" , "ANALYSIS" , "SYNTHESIS" , "EVALUATION"]
connection = neo4j.connect("http://localhost:7474")
cursor = connection.cursor()
s = 'MATCH (d:`Domain`)-[]-(v:`Verb`) WHERE d.OldTerminology = "{}" RETURN v '
domain = { "KNOWLEDGE" : {0} , "COMPREHENSION" : {0} , "APPLICATION" : {0} , "ANALYSIS" : {0} , "SYNTHESIS" : {0} , "EVALUATION" : {0} }

for d in domain.keys():
    s = s.format(d)
    x = cursor.execute(s)
    for i in x:
       domain[d].add(i[0]['verb'])
    domain[d].remove(0)
    s = 'MATCH (d:`Domain`)-[]-(v:`Verb`) WHERE d.OldTerminology = "{}" RETURN v '

with open("NewDomainVector.txt",'w') as fp:
    fp.write(repr(domain))
'''
domain = {"KNOWLEDGE":{"Write", "List", "Label", "Name", "State", "Define", "Count", "Describe", "Draw", "Find", "Identify", "Match", 
                        "Quote", "Recall", "Recite", "Sequence", "Tell", "Arrange", "Duplicate", "Memorize", "Order", "Outline", 
                        "Recognize", "Relate", "Repeat", "Reproduce", "Select", "Choose", "Copy", "How", "Listen", "Locate",
						"Memorise", "Observe", "Omit", "Read", "Recognise", "Record", "Remember", "Retell", "Show", "Spell",
						"Trace", "What", "When", "Where", "Which", "Who", "Why"},
          "COMPREHENSION":{"Explain", "Summarize", "Paraphrase", "Describe", "Illustrate", "Conclude", "Demonstrate", "Discuss",
						   "Generalize", "Identify", "Interpret", "Predict", "Report", "Restate", "Review", "Tell", "Classify",
						   "Convert", "Defend", "Distinguish", "Estimate", "Express", "Extend", "Give example", "Indicate",
						   "Infer", "Locate", "Recognize", "Rewrite", "Select", "Translate", "Ask", "Cite", "Compare",
						   "Contrast", "Generalise", "Give examples", "Match", "Observe", "Outline", "Purpose", "Relate",
						   "Rephrase", "Show", "Summarise"},
          "APPLICATION":{"Use", "Compute", "Solve", "Demonstrate", "Apply", "Construct", "Change", "Choose", "Dramatize", "Interview",
						 "Prepare", "Produce", "Select", "Show", "Transfer", "Discover", "Employ", "Illustrate",
						 "Interpret", "Manipulate","Modify", "Operate", "Practice", "Predict", "Relate schedule", "Sketch",
						 "Use write", "Act", "Administer", "Associate", "Build", "Calculate", "Categorise", "Classify",
						 "Connect", "Correlation", "Develop", "Dramatise", "Experiment", "With", "Group", "Identify",
						 "Link", "Make use of", "Model", "Organise", "Perform", "Plan", "Relate", "Represent", "Simulate",
						 "Summarise", "Teach", "Translate"},
          "ANALYSIS":{"Analyse", "Categorize", "Compare", "Contrast", "Separate", "Characterize", "Classify", "Debate", "Deduce", 
					  "Diagram", "Differentiate", "Discriminate", "Distinguish", "Examine", "Outline", "Relate", "Research", 
					  "Appraise", "Breakdown", "Calculate", "Criticize", "Derive", "Experiment", "Identify", "Illustrate", 
					  "Infer", "Interpret", "Model", "Outline", "Point out", "Question", "Select", "Subdivide", "Test", 
					  "Arrange", "Assumption", "Categorise", "Cause and", "Effect", "Choose", "Difference", "Discover", 
					  "Dissect", "Distinction", "Divide", "Establish", "Find", "Focus", "Function", "Group", "Highlight", 
					  "In-depth", "Discussion", "Inference", "Inspect", "Investigate", "Isolate", "List", "Motive", "Omit", 
					  "Order", "Organise", "Point out", "Prioritize", "Rank", "Reason", "Relationships", "Reorganise", "See", 
					  "Similar to", "Simplify", "Survey", "Take part in", "Test for", "Theme", "Comparing"},
          "SYNTHESIS":{"Create", "Design", "Hypothesize", "Invent", "Develop", "Compose", "Construct", "Integrate", "Make",
					   "Organize", "Perform", "Plan", "Produce", "Propose", "Rewrite", "Arrange", "Assemble", "Categorize", 
					   "Collect", "Combine", "Comply", "Devise", "Explain", "Formulate", "Generate", "Prepare", "Rearrange",
					   "Reconstruct", "Relate", "Reorganize", "Revise", "Set up", "Summarize", "Synthesize", "Tell", "Write", 
					   "Adapt", "Add to", "Build", "Change", "Choose", "Combine", "Compile", "Convert", "Delete", "Discover", 
					   "Discuss", "Elaborate", "Estimate", "Experiment", "Extend", "Happen", "Hypothesise", "Imagine",
					   "Improve", "Innovate", "Make up", "Maximise", "Minimise", "Model", "Modify", "Original", "Originate",
					   "Predict", "Reframe", "Simplify", "Solve", "Speculate", "Substitute", "Suppose", "Tabulate", "Test", 
					   "Theorise", "Think", "Transform", "Visualise"},
          "EVALUATION":{"Judge", "Recommend", "Critique", "Justify", "Appraise", "Argue", "Assess", "Choose", "Conclude", 
						"Decide", "Evaluate", "Predict", "Prioritize", "Prove", "Rank", "Rate", "Select", "Attach", "Compare", 
						"Contrast", "Defend", "Describe", "Discriminate", "Estimate", "Explain", "Interpret", "Relate",
						"Summarize", "Support", "Value", "Agree", "Award", "Bad", "Consider", "Convince", "Criteria", 
						"Criticise", "Debate", "Deduct", "Determine", "Disprove", "Dispute", "Effective", "Give reasons", "Good",
						"Grade", "How do we", "Know", "Importance", "Infer", "Influence", "Mark", "Measure", "Opinion", 
						"Perceive", "Persuade", "Prioritise", "Rule on", "Test", "Useful", "Validate", "Why"}
          }

'''
with open("tmp","a") as f:
    f.write(str(domain))

levels = {
              "KNOWLEDGE" : 0,
              "COMPREHENSION" : 0,
              "APPLICATION" : 0,
              "ANALYSIS" : 0,
              "SYNTHESIS" : 0,
              "EVALUATION" : 0
         }



t = blessings.Terminal()
p = 0


if len(sys.argv) > 1:

    print t.underline("Coloring Scheme")
    for i in domainNames:
        print colour(i.title(),i),"Domain"

    print " "
    print t.underline("Question Paper")
    print " "
    
    if os.path.exists(sys.argv[1].replace('Question','Answer')):
        answers = [i.strip().split(' ') for i in open(sys.argv[1].replace('Question','Answer'),'r') if i != '\n' ]

    with open(sys.argv[1]) as fp:
        question_number = ''
        dom_to_question = {}
        for i in fp.readlines():
            i = i[:-1]
            x = i.split(' ')
            matched = False
            question_numbers = re.search(r'(\d[\w]?\.)',i);
            if question_numbers:
                question_number = question_numbers.groups()
            elif i[:5] == '    i':
                question_numbers = True    
            
            list_of_doms = []
            for k,j in enumerate(x):
                orij = j
                x[k] = check_in_dict(j)+j
                if x[k] == orij: 
                    x[k] = check_for_synonyms(j)+j
                            
            for k,j in enumerate(x):  
                y = j.split('@')
                if len(y)>1:
                    list_of_doms = y[:-1]
                    for word in y[:-1]: 
                        accumulate(word)
                    y[-1]+='@'+y[-2]
                x[k] = y[-1]
                
                if question_number != '':
                    try:
                        dom_to_question[question_number[0]].update(list_of_doms)
                    except:
                        dom_to_question[question_number[0]] = set(list_of_doms)
            
            
            for i in x:
                if '@' in i:
                    y = i.split('@')
                    #print y
                    i = y[0]
                    print colour(y[0],y[1]),
                else:
                    print i,
            print ''
            
            
    total_levels = 0
    total_sum = 0
    cumulative_sum = 0
    weighted_average = 0
    print " "
    print t.underline("Final Aggregate Points")
    print " "
    for v,i in enumerate(domainNames):
        print colour(i.title(),i),levels[i]
        total_levels += levels[i]
        cumulative_sum += levels[i] * (v+1)
    
    print "The total number of points earned is       : {}".format(total_levels)
    print "The cumulative sum of the points earned is : {}".format(cumulative_sum)
    print "The aggregate score of the paper is        : {:.2f}".format(cumulative_sum / (total_levels * 1.0))
    
    os.system('figlet Aggregate {:.2f}'.format(cumulative_sum / (total_levels * 1.0)))
              
    print " "
    print t.underline("Final Student Attributes")
    print " "
    domNames = copy.copy(domainNames)
    random.shuffle(domNames)
    for i in domNames:
        if levels[i] >0 :
            print getlevelDefinition(i)      
            
    if os.path.exists(sys.argv[1].replace('Question','Answer')):
        if '/' in answers[0][1]:
            open('loads.json','w').close()
            for i in sorted(dom_to_question):
                marks = [j[1] for j in answers if j[0] == i]
                mo,mm = marks[0].split('/')
                dump_json(i,mo,mm,list(dom_to_question[i]))
        else:
            try:
                print t.underline("\nPredicted Marks for the subject\n")
                marks_per_domain = {j:sum(i['marks_obtained'] for i in read_json_by_domains(j)) for j in domainNames}
                max_marks_per_domain = {j:sum(i['maximum_marks'] for i in read_json_by_domains(j)) for j in domainNames}
                marking_scheme = {j[0]:int(j[1]) for j in answers}
                mapping_value_per_domain = {j:marks_per_domain[j]/float(max_marks_per_domain[j]) for j in domainNames}
                predicted_marks = {i:0 for i in marking_scheme}
                for i,v in dom_to_question.items():
                    maximum_marks = marking_scheme[i]
                    for j in v:
                        predicted_marks[i]+=mapping_value_per_domain[j]*marking_scheme[i]
                    predicted_marks[i] = predicted_marks[i]/len(v)
                for i,v in sorted(predicted_marks.items()):
                    print '{}  {:.2f}'.format(i,v)
                total_predicted_marks = sum(v for i,v in predicted_marks.items())
                #print t.underline("\nTotal Marks"),
                #print '{:.2f}\n'.format(total_predicted_marks)
                print t.underline("\nExpected Marks Range"),
                print '{:.2f} to {:.2f}\n '.format(total_predicted_marks*0.95,total_predicted_marks*1.05)
                
                os.system('figlet Total Marks {:.2f}'.format(total_predicted_marks))
                    
            except Exception as e:
                print e
    multiprocessing.Process(target = draw).start()
    
else:
    ques = raw_input("Enter your question here\n");
    x = ques.split()
    list_of_doms = []
    for k,j in enumerate(x):
        orij = j
        x[k] = check_in_dict(j)+j
        '''if x[k] == orij: 
            x[k] = check_for_synonyms(j)+j'''
                    
    for k,j in enumerate(x):  
        y = j.split('@')
        if len(y)>1:
            list_of_doms = y[:-1]
            for word in y[:-1]: 
                accumulate(word)
            y[-1]+='@'+y[-2]
        x[k] = y[-1]
        
    for i in x:
        if '@' in i:
            y = i.split('@')
            #print y
            i = y[0]
            print colour(y[0],y[1]),
        else:
            print i,
    print ''
    
    total_levels = 0
    total_sum = 0
    cumulative_sum = 0
    weighted_average = 0
    print " "
    print t.underline("Final Aggregate Points")
    print " "
    for v,i in enumerate(domainNames):
        print colour(i.title(),i),levels[i]
        total_levels += levels[i]
        cumulative_sum += levels[i] * (v+1)
    
    multiprocessing.Process(target = draw).start()
