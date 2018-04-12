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
import pycurl
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
    problem_names = open('C:\Github\pythonScripts\MSlibrary-generation\problem_names.txt','w')
    
    
    inchikey_list = []
    #Iterate through each line and access each individual URL
    for item in met_list:
        buffer = BytesIO()
        c = pycurl.Curl()
        url = 'http://cts.fiehnlab.ucdavis.edu/rest/convert/Chemical%20Name/InChiKey/' + item[0:-1]
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()

        body = buffer.getvalue()
        # Body is a byte string.
        # We have to know the encoding in order to print it to a text file
        # such as standard output.
        
        #NEED TO HANDLE EXCEPTIONS WHEN MULTIPLE INCHIKEYS COME UP AND WHEN NONE COME UP
        out = str(body.decode('iso-8859-1')) #For ~40% of metabolites, this is coming back showing a bad URL request

        try:
            out = json.loads(out)
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
    #input - .txt file containing InChiKeys - 1 per line
    #Input type - file
    #Output - .msl file with filtered Golm MS library
    #Output type - .msl file
    keys = open(inchikey_file_path,'r')
    gmd = open(libfile_path,'r')
    keys = keys.readlines() #creates a list of strings that are InChiKeys + \n character
    

    #Remove the part of the InChiKey denoting protonation state (last character)
    for key in keys:
        key = key[0:-3]

    gmd = gmd.readlines()
    newfile = open(outputfile_path,'w')
    entry = ['']
    GMDinchikeys = ['']
    j = 0
    for line in gmd:
        if not line == '\n':
            entry[j] = entry[j] + line
            #if line.startswith('MET_INCHIKEY'):
                #GMDinchikeys[j] = line[-29:-3] #remove the charge descriptor since not necessary for matching here
        else:        
            entry.append('')
            j = j+1            
               
    

    #Now have a list of strings that are the library blocks
    #Iterate through each block and check for InChiKey. Block with no InChiKey, add to library
    inchis_not_in_GMD = []
    for block in entry:
        #Check if block has an InChiKey
        block_key_idx = block.find('MET_INCHIKEY')
        
        #print(block_key)
        if not block_key_idx == -1:
            block_key = block[block_key_idx+14:block_key_idx+42]
            if block_key in key:
                newfile.write(block + '\n')
                break
            
                    

        else:
            newfile.write(block + '\n')
                
    return list(set(inchis_not_in_GMD))


def test():
    '''
    This function tests and collects metrics on the generated library

    '''
    #translate_to_INCHIKeys()
    not_in_GMD = filterGMD('C:\Github\pythonScripts\MSlibrary-generation\InChiKeys_iAF1260b_combined.txt','C:\Github\pythonScripts\MSlibrary-generation\GMD-20111121_Var5_ALK.msl','C:\Github\pythonScripts\MSlibrary-generation\GMD_iAF1260b.msl')
    print(len(not_in_GMD))
    
    




  
def main():
    test()
    #filterGMD('C:\Github\pythonScripts\MSlibrary-generation\InChiKeys.txt','C:\Github\pythonScripts\MSlibrary-generation\GMD-20111121_Var5_ALK.msl','C:\Github\pythonScripts\MSlibrary-generation\Testoutput.msl')
    



if __name__ == "__main__":
    main()
   
   
   

   
  
	
	