#Testing out metabolite name extraction from xml and json files

import json

input_file = open('Downloads\iAPECO1_1312.json','r')
output_file = open('test.txt','w')
#print(fil)
   
model = json.load(input_file)

metabolite_list = model.get('metabolites') #this is a list of json data

metabolites = []
for item in metabolite_list:
   met = item.get('name')
   metabolites.append(met) 
     
metabolites = list(set(metabolites)) #set removes duplicate values
   

output_file.write(str(metabolites)) #produces a list of names that needs to be cross-referenced with NIST

#Consider other identifiers if possible. Other option is formula. No more detail available

   
  
	
	