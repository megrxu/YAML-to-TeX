from models import Command, Environment, Document
from yaml import load


input_yml = open('example.yml', 'r', encoding=('utf8'))
root = load(input_yml)

output_file = 'example.tex'

doc = Document(root)
doc.texize()
doc.dump()

tex = open( output_file, 'w', encoding=('utf-8'))
tex.write(doc.tex)
tex.close()