''' Mass spec library curation using information derived from KBase

BUGS:
1. (stereo)Isomer SMILES keys are not differentiable (example maleylpyruvate and 3-fumarylpyruvate)
*KEGG IDs are not repeated when SMILES are repeated and InChiKeys are NOT repeated

Repeated SMILES (different InChiKeys):
maleylpyruvate, 3-fumarylpyruvate
2-keto-3-deoxygluconate_c0, 2-Dehydro-3-deoxy-D-galactonate_c0
R-acetoin, S-acetoin
D-mannitol-1-phosphate_c0, Galactitol 1-phosphate_c0
D-fructose-6-phosphate_c0, D-Tagatose 6-phosphate_c0, L-Tagatose 6-phosphate_c0
D-fructose-1,6-bisphosphate_c0, D-Tagatose 1,6-biphosphate_c0
L-Fuculose_c0, L-Rhamnulose_c0
L-Fuculose-1-phosphate_c0, L-Rhamnulose-1-phosphate_c0
Glucose-1-phosphate_c0, D-Mannose1-phosphate_c0, alpha-D-Hexose 1-phosphate_c0, beta-D-Glucose 1-phosphate_c0, D-Galactose 1-phosphate_c0
UDP-glucosamine_c0, UDP-galactosamine_c0
gluconate_c0, D-Altronate_c0, L-Idonate_c0, D-Mannonate_c0
LL-2,6-Diaminopimelate_c0, meso-2,6-Diaminopimelate_c0
D-Mucic acid_c0, D-Glucarate_c0
5-Dehydro-4-deoxy-D-glucarate_c0, 2-Dehydro-3-deoxy-D-glucarate_c0
Retinol_c0, 11-cis-Retinol_c0
Retinol palmitate_c0, 11-cis-Retinyl palmitate_c0
CDPparatose_c0, CDPtyvelose_c0
D-methylmalonyl-CoA_c0, L-methylmalonyl-CoA_c0
(R)-Allantoin_c0, Allantoin_c0
UDP-N-acetylglucosamine_c0, UDP-N-acetyl-D-galactosamine_c0, UDP-N-acetyl-D-mannosamine_c0, 
cellobiose, lactose
L-ribulose-5-phosphate_c0, D-Xylulose5-phosphate_c0, D-Ribulose5-phosphate_c0, L-Xylulose 5-phosphate_c0
D-Ribulose_c0, L-Ribulose_c0, D-Lyxulose_c0, L-Lyxulose_c0
(R)-1,2-Propanediol_c0, 1,2-Propanediol_c0
D-Lactaldehyde_c0, L-Lactaldehyde_c0
cis-Aconitate_c0, trans-Aconitate_c0
GDP-mannose, GDP-glucose
(R)-(+)-Citronellal_c0, (S)-(-)-Citronellal_c0


'''


import pandas as pd
import xlrd
import requests
from io import BytesIO

xls = pd.ExcelFile('escherichia_coliMG1655_mets.xlsx')

sheetX = xls.parse(0) #2 is the sheet number

inchiKeys = sheetX['inchikey'] #Original length = 1275 InChiKeys for E coli model
smiles = sheetX['smiles']

inchiKeys = list(set(inchiKeys)) #After removing duplicates, 908 InChiKeys for E coli model. Assuming this removes <compound>_c0 and <compound>_e0 duplicates


url = 'https://www.chemspider.com/InChI.asmx?op=InChIKeyToInChI'
headers = {'content-type': 'text/xml'}
body = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <InChIKeyToInChI xmlns="http://www.chemspider.com/">
      <inchi_key>""" +inchiKeys[1]+"""</inchi_key>
    </InChIKeyToInChI>
  </soap:Body>
</soap:Envelope>"""
#print(body)
response = requests.post(url,data=body,headers=headers)
txt = BytesIO(response.content)
txt = txt.getvalue().decode('utf-8')
idx = txt.find('InChI=')
inchi = ''
while True:
    if txt[idx] == '<':
        break
    else:
        inchi = inchi + txt[idx]
        idx = idx+1
print (txt)
print(inchi)



