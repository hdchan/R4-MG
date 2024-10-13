from urllib.request import urlopen
import json
response = urlopen("https://www.dropbox.com/scl/fi/zz5zyil3ibwda0r3f8799/test.json?rlkey=mn2y600rrmledbfhrjk05a9ba&dl=0&raw=1")
json_response = json.load(response)
print(json_response['key'])