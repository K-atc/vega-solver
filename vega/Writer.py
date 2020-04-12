class Writer:
    pass

class StringWriter(Writer):
    def __init__(self):
        self.out = []
    
    def write(self, content):
        self.out.append(content)

    def finalize(self):
        return '\n'.join(self.out) + '\n'

class FileWriter(Writer):
    def __init__(self, file):
        self.out = file

    def write(self, content):
        self.out.write(content + '\n')
    
    def finalize(self):
        return None