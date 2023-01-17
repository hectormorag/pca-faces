class OBJFastV:
    def __init__(self, filename):
        self.vertices = []

        for line in open(filename, "r"):
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'v':
                v = float(values[1]),float(values[2]),float(values[3])
                self.vertices.append(v)

class OBJ:
    def __init__(self, filename):
        
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []
        self.mtlfile = []
        self.material = []
        material = None
        
        for line in open(filename, "r"):
            
            # if line starting with #, skip
            if line.startswith('#'): continue

            # split line (separate each info between spaces)
            values = line.split()
            
            # if empty line, skip
            if not values: continue
            
            # if line starting with v
            if values[0] == 'v':
                v = float(values[1]),float(values[2]),float(values[3])
                self.vertices.append(v)
                
            # if line starting with vn
            elif values[0] == 'vn':
                vn = float(values[1]),float(values[2]),float(values[3])
                self.normals.append(vn)
                
            # if line starting with vt
            elif values[0] == 'vt':
                vt = float(values[1]),float(values[2])
                self.texcoords.append(vt)
                
            # if line starting with usemtl / usemat
            elif values[0] in ('usemtl', 'usemat'):
                material = values[1]
                self.material = material
                
            # if line starting with f
            elif values[0] == 'f':
                face = []
                texcoords = []
                norms = []
                
                for f in values[1:]:
                    # split line again (separate each info between /  )
                    val = f.split('/')
                    face.append(int(val[0]))
                    if len(val) >= 2 and len(val[1]) > 0:
                        texcoords.append(int(val[1]))
                    else:
                        texcoords.append(0)
                        
                    if len(val) >= 3 and len(val[2]) > 0:
                        norms.append(int(val[2]))
                    else:
                        norms.append(0)
                self.faces.append((face, norms, texcoords, material))














                    
                                
