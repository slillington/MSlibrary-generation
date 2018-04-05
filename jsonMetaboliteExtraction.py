#Testing out metabolite name extraction from xml and json files
'''
Things this script needs to accomplish
1. Isolate metabolite names from BiGG genome-scale model .json file
2. Convert metabolite names to InCHI Keys (done using Fiehn Lab Chemical Translation Service)
3. Search .msl file for InCHI keys and create new library file with only matching entries

'''


import json
import pycurl
from io import BytesIO

def pullMetabolites():
    #This function outputs a list of the names of metabolites in a BiGG database genome-scale model (.json format)
    input_file = open('C:\GitHub\pythonScripts\MSlibrary-generation\iAF1260b.json','r')
    output_file = open('metabolite_names.txt','w')
    #print(fil)
   
    model = json.load(input_file)

    metabolite_list = model.get('metabolites') #this is a list of json data

    metabolites = []
    for item in metabolite_list:
        met = item.get('name')
        metabolites.append(met) 
     
    metabolites = list(set(metabolites)) #set removes duplicate values
    for it in metabolites:
	    output_file.write(it + '\n')
		
    #output_file.write(str(metabolites)) #produces a list of names that needs to be cross-referenced with NIST
    #Consider other identifiers if possible. Other option is formula. No more detail available
    return metabolites
   

#Translate names to InCHIKeys
def translate_to_INCHIKeys():
    input = open('C:\GitHub\pythonScripts\MSlibrary-generation\metabolite_names_test.txt','r')
    met_list = input.readlines()
    buffer = BytesIO()
    c = pycurl.Curl()
    
    inchikey_list = []
    #Iterate through each line and access each individual URL
    for item in met_list:
        print(item)
        c.setopt(c.URL, 'http://cts.fiehnlab.ucdavis.edu/rest/score/Chemical%20Name/' + item + '/biological')
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        #c.close()

        body = buffer.getvalue()
        # Body is a byte string.
        # We have to know the encoding in order to print it to a text file
        # such as standard output.
        
        #NEED TO HANDLE EXCEPTIONS WHEN MULTIPLE INCHIKEYS COME UP AND WHEN NONE COME UP
        out = body.decode('iso-8859-1')
        out = json.loads(out)
        #print(out)
        out = out['result']
        out = out[0]
        out = out['InChiKey']
        inchikey_list.append(out)
    c.close()
    input.close()
    print(inchikey_list)
    return	

'''	
#Need a function to isolate entries in the .msl file and search whether the identifiers match or not
def searchGMD(keys,msl_file):
    #This function reads the .msl file containing mass spec info, searches it for InCHI keys matching those in the input .txt file
	#and outputs a .msl file with the specific library entries
'''
   
def main():
    #temp = pullMetabolites()
    #print(temp)
	translate_to_INCHIKeys()
    



if __name__ == "__main__":
    main()
   
   
   

   
  
	
	