import requests
r = requests.get('https://github.com/hdchan/R4-MG/releases/latest') 
print(requests.utils.urlparse(r.url).path)