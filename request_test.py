#Test requests package

import pubchempy as pcp
import pandas as pd

#url = 'http://cts.fiehnlab.ucdavis.edu/rest/convert/Chemical%20Name/InChiKey/Maltotriose C18H32O16'

#r = requests.get(url)
#print(r.status_code)
#print(r.headers['content-type'])
#print(r.encoding)
#print(r.text)
#print(r.json())
def get_model_data(excel_file_path):

#get_model_data take the list of inchikeys and smiles from an excel file that contains the .tsv download from KBASE. This .tsv download has information
#on the metabolites in a genome-scale metabolic model.
#type input: string
#input: file path to excel file containing model metabolite information
#type output inchiKeys: list of InChiKeys (type string) in the model
#type output smiles: list of SMILES (type string) in the model   

    #xls = pd.ExcelFile('escherichia_coliMG1655_mets.xlsx')
	xls = pd.ExcelFile(excel_file_path)
	sheetX = xls.parse(0) #2 is the sheet number

	inchiKeys = sheetX['inchikey'] #Original length = 1275 InChiKeys for E coli model
	smiles = sheetX['smiles']

	inchiKeys = list(set(inchiKeys)) #After removing duplicates, 908 InChiKeys for E coli model. Assuming this removes <compound>_c0 and <compound>_e0 duplicates
	inchiKeys = [x for x in inchiKeys if not str(x) in ['NaN','nan']]
	inchiKeys.sort()
	
	return inchiKeys, smiles
	
	

inChiKeys = open(r'C:\GitHub\pythonScripts\Mtb_inhibition\Mtb_inhibition\trouble_keys_file.txt','r')
iso_smiles = []
keys_not_in_PubChem = []
for key in inChiKeys:
	#print(key)
	try:
		result = pcp.get_compounds(key[0:-1],'inchikey')
	except:
		keys_not_in_PubChem.append(key)
		continue
	#print(result)
	if result:
		iso_smiles.append(result[0].isomeric_smiles)
	else:
		print(key)

print(keys_not_in_PubChem)		
#print(iso_smiles)
