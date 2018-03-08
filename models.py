class TeXEntity():
  def __init__(self, name: str, params: list=[], options: list=[], content: list=[]):
    self.name = name
    self.params = params
    self.options = options
    self.content = content
    self.texize()

  def texize(self):
    self.name_tex = '\\' + self.name
    if self.params:
      self.params_tex = ''.join(['{' + item + '}' for item in self.params]
                                if type(self.params) is list else '{' + self.params + '}')
    else:
      self.params_tex = ""
    self.options_tex = '[' + \
        ','.join(self.options) + ']' if self.options else ''
    if not self.content:
      self.content_tex = ""
    elif type(self.content) is str:
      self.content_tex = '' + self.content
    elif type(self.content) is list:
      content_tex = []
      for item in self.content:
        if type(item) is str:
          content_tex.append(item)
        else:
          content_tex.append(item.dump())
      self.content_tex = '' + '\n'.join(content_tex)
    else:
      self.content_tex = '' + self.content.dump()


class Command(TeXEntity):
  def dump(self):
    if self.options_tex == '' and (len(self.params) if type(self.params) is list else 1) <= 1 and self.name != 'begin':
      self.tex = self.name_tex + self.params_tex + ' ' + self.content_tex
    else:
      self.tex = self.name_tex + self.options_tex + \
          self.params_tex + '\n\n' + self.content_tex
    return self.tex


class Environment(TeXEntity):
  def dump(self):
    self.texize()
    self.tex = '\n\n'.join(
        [self.begin.dump(), self.end.dump()])
    return self.tex

  def texize(self):
    self.begin = Command('begin', [self.name] +
                         self.params, self.options, self.content)
    self.end = Command('end', self.name)
    self.content_tex = self.begin.content_tex


class Document(TeXEntity):
  def __init__(self, root):
    self.name = 'documentclass'
    self.config = root['config']
    self.document = root['document']
    self.init()
    self.load_config()
    self.load_document()
    self.texize()

  def init(self):
    self.params = self.config['documentclass']['name']
    self.options = self.config['documentclass']['options']
    self.content = []
    return

  def load_config(self):
    if 'packages' in self.config.keys():
      self.content += packages_handler(self.config['packages'])
    self.content += commands_handler(self.config['precommands'])
    return

  def load_document(self):
    content = []
    content += commands_handler(self.document['precommands'])
    content += parse_nodes(self.document['schema']['root'], self.document['schema']['environments'], self.document['schema']['commands'])
    document = Environment(name='document', content = content)
    self.content += ['', document]
    return

  def dump(self):
    if self.options_tex == '' and (len(self.params) if type(self.params) is list else 1) <= 1 and self.name != 'begin':
      self.tex = self.name_tex + self.params_tex + ' ' + self.content_tex
    else:
      self.tex = self.name_tex + self.options_tex + \
          self.params_tex + '\n\n' + self.content_tex
    return self.tex


def packages_handler(packages):
  packages_list = []
  for item in packages:
    packages_list.append(package_handler(item))
  return packages_list


def package_handler(package):
  if type(package) is str:
    return Command('usepackage', params=package)
  else:
    return Command('usepackage', params=package['name'], options=package['options'])


def commands_handler(commands):
  commands_list = []
  for item in commands:
    commands_list.append(command_handler(item))
  return commands_list


def command_handler(command):
  if type(command) is str:
    return Command(command)
  elif type(command) is dict:
    name = list(command.keys())[0]
    if type(command[name]) is str:
      return Command(name, params=command[name])
    else:
      command = command[name]
      params = command['params'] if 'params' in command.keys() else []
      options = command['options'] if 'options' in command.keys() else []
      return Command(name, params=params, options=options)

def parse_nodes(nodes, environments, commands):
  if type(nodes) is str:
    return [nodes]
  return [parse_node(node, environments, commands) for node in nodes]

def parse_node(node, environments, commands):
  if type(node) is dict:
    node_name = list(node.keys())[0]
    node = node[node_name]
    if type(node) is str:
      return Command(node_name, params=node)
    else:
      content = parse_nodes(node['content'], environments, commands) if 'content' in node.keys() else []
      params = node['params'] if 'params' in node.keys() else []
      options = node['options'] if 'options' in node.keys() else []
  elif type(node) is str:
    return node
  if node_name in environments:
    return Environment(node_name, params=params, options=options, content=content)
  elif node_name in commands:
    return Command(node_name, params=params, options=options, content=content)


