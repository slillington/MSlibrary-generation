#Testing out metabolite name extraction from xml and json files
'''
Things this script needs to accomplish
1. Isolate metabolite names from BiGG genome-scale model .json file
2. Convert metabolite names to InCHI Keys
3. Search .msl file for InCHI keys and create new library file with only matching entries

'''


import json
	
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
   

#Need a function to isolate entries in the .msl file and search whether the names match or not
   
def main():
    temp = pullMetabolites()
    print(temp)
    



if __name__ == "__main__":
    main()
   
   
   

   
  
	
	