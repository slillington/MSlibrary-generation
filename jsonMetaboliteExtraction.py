#Testing out metabolite name extraction from xml and json files
'''
Things this script needs to accomplish
1. Isolate metabolite names from BiGG genome-scale model .json file
2. Convert metabolite names to InCHI Keys (done using Fiehn Lab Chemical Translation Service)
3. Search .msl file for InCHI keys and create new library file with only matching entries
4. Publish metrics
	- How many metabolites did not have a corresponding InChiKey?
	- Of those that did have an InChiKey, which are not contained in the Golm library?
5. Attempt to replace unknowns
	a. Metabolites that didn't have an InChiKey
		i. Analyze for key words ('CoA','tRNA', etc.)
		ii. Obtain a SMILE and "derivatize" using MetaboloDerivatizer
	b. Metabolites that are "Unknown" in Golm
		i. Use the m/z ratios to search NIST for the metabolite

'''


import json
import requests
from io import BytesIO

def pullMetabolites():
    #This function outputs a list of the names of metabolites in a BiGG database genome-scale model (.json format)
    #Also output is the number of metabolites in the metabolic model
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
    return len(metabolites), metabolites
   

#Translate names to InCHIKeys
def translate_to_INCHIKeys():
    '''
    translate_to_INCHIKeys takes a text file containing metabolite names and uses the Chemical Translation Service (Fiehn Lab, UC Davis)
    to search PubChem for an InChiKey for each metabolite name. For names that produce multiple InChiKeys, only the first (presumably the highest scoring match) is selected.
    output: InChiKeys.txt
    output type: .txt file

    BUGS:
    - PyCurl not working for many metabolites. For some reason the address is returning nothing - not even the string representing the query that contains "results":[]
    '''
    input = open('C:\GitHub\pythonScripts\MSlibrary-generation\metabolite_names.txt','r')
    met_list = input.readlines()
    problem_names = open('C:\Github\pythonScripts\MSlibrary-generation\problem_namesNEW.txt','w')
    
    
    inchikey_list = []
    #Iterate through each line and access each individual URL
    for item in met_list:
        url = 'http://cts.fiehnlab.ucdavis.edu/rest/convert/Chemical%20Name/InChiKey/' + item[0:-1]
        r = requests.get(url)
        if not r.status_code == 200:
            problem_names.write(item)
            continue
        
        

        try:
            out = r.json()
            #print(out)
            out = out[0]
            out = out['result']
            if not out:
                inchikey_list.append('NotFound_in_PubChem')
            else:
                out = out[0]
                inchikey_list.append(out)
        except:
            problem_names.write(item)
            
            
    
    input.close()
    #print(inchikey_list)
    #output InChiKey list to text file to be read for .msl file filtering
    output_file = open('InChiKeys_iAF1260b.txt','w')
    for key in inchikey_list:
        output_file.write(key + '\n')
    
    output_file.close()
    return	

'''	
#Need a function to isolate entries in the .msl file and search whether the identifiers match or not
def searchGMD(keys,msl_file):
    #This function reads the .msl file containing mass spec info, searches it for InCHI keys matching those in the input .txt file
	#and outputs a .msl file with the specific library entries
    Output type - list
    Output - list of InChiKeys from model for which there was no entry in the Golm database
'''
 

def filterGMD(inchikey_file_path, libfile_path, outputfile_path):
    '''
BUGS: 1. InChiKeys produced from CTS refer to compounds that are in Golm, but have different InChiKeys (e.g. amino acid isomers - DL- vs L- vs D-)

    '''
    #input - .txt file containing InChiKeys - 1 per line
    #Input type - file
    #Output - .msl file with filtered Golm MS library
    #Output type - .msl file
    keys = open(inchikey_file_path,'r')
    gmd = open(libfile_path,'r')
    keys = keys.readlines() #creates a list of strings that are InChiKeys + \n character
    keys2 = [] #list of keys without protonation state
    for k in keys:
        keys2.append(k[0:-2]) #Remove the part of the InChiKey denoting protonation state (last character)

    keys2 = list(set(keys2))

    gmd = gmd.readlines()
    newfile = open(outputfile_path,'w')
    entry = ['']
    GMDinchikeys = ['']
    j = 0
    for line in gmd:
        if not line == '\n':
            entry[j] = entry[j] + line
            #if line.startswith('MET_INCHIKEY'):
               # GMDinchikeys.append(line[-28:-2]) #remove the charge descriptor since not necessary for matching here
        else:        
            entry.append('')
            j = j+1            
               

    #Now have a list of strings that are the library blocks
    #Iterate through each block and check for InChiKey. Block with no InChiKey, add to library
    #inchis_not_in_GMD = []
    for block in entry:
        #Check if block has an InChiKey
        block_key_idx = block.find('MET_INCHIKEY')
        
        if not block_key_idx == -1:
            block_key = block[block_key_idx+14:block_key_idx+40]
            GMDinchikeys.append(block_key) #These inchikeys do not contain the very last character
            if block_key in keys2:
                newfile.write(block + '\n')
            
        else:
            newfile.write(block + '\n')
    #print(keys2)
    #Write InChiKeys not in GMD to a txt file to translate back to names using CTS
    output2 = open('C:\Github\pythonScripts\MSlibrary-generation\inchikeys_not_in_GMD.txt','r+')
    not_in_GMD = []

    for i in keys2: 
        if not i in GMDinchikeys:
            #output2.write(i + 'N\n')
            not_in_GMD.append(i+'N')
        else:
            print(i)

    not_in_GMD = list(set(not_in_GMD))
    for k in not_in_GMD:
        output2.write(k+'\n')
    
     
               
    return


def test():
    '''
    This function tests and collects metrics on the generated library

    '''
    #length, met_list = pullMetabolites()
    #print(length)
    #translate_to_INCHIKeys()
    not_in_GMD = filterGMD('C:\Github\pythonScripts\MSlibrary-generation\InChiKeys_iAF1260b.txt','C:\Github\pythonScripts\MSlibrary-generation\GMD-20111121_Var5_ALK.msl','C:\Github\pythonScripts\MSlibrary-generation\GMD_iAF1260bNEW.msl')
    #For E coli iAF1260b, 828 metabolites in the model are not found in Golm
    
    




  
def main():
    test()
    


if __name__ == "__main__":
    main()
   
   
   

   
  
	
	