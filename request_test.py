#Test requests package

import requests

url = 'http://cts.fiehnlab.ucdavis.edu/rest/convert/Chemical%20Name/InChiKey/Maltotriose C18H32O16'

r = requests.get(url)
print(r.status_code)
print(r.headers['content-type'])
print(r.encoding)
print(r.text)
print(r.json())
