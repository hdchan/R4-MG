from PIL import Image
filename = 'AppUI/resources/logo-orig.png'
img = Image.open(filename)
icon_sizes = [(16,16), (32, 32), (48, 48), (64,64), (128, 128), (256, 256)]
img.save('favicon.ico', sizes=icon_sizes)