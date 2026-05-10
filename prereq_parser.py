mat237 = "<p>[MAT133Y1/ (MAT130H1/ MAT135H1, MAT136H1)/ (MAT135H5, MAT136H5)/ (MATA30H3/ MATA31H3, MATA36H3), MAT138H1/ MAT102H5/ MAT246H1]/ (MAT148H1, MAT149H1)/ MAT137Y1/ MAT137Y5/ (MAT137H5, MAT139H5)/ (MATA30H3/ MATA31H3, MATA37H3)/ (MAT158H1, MAT159H1)/ MAT157Y1/ MAT157Y5/ (MAT157H5, MAT159H5), MAT223H1/ MATA22H3/ MATA23H3/ MAT240H1/ MAT240H5</p>"
csc111 = "CSC110Y1 (70% or higher)"
sta272 = "<p>CSC108H1/ CSC110Y1/ CSC148H1, STA220H1/ ECO220Y1/ ECO227Y1/ GGR270H1/ IRW220H1/ PSY201H1/ SOC202H1/ STA261H1/ STA238H1/ STA248H1/ STA288H1/ EEB225H1</p>"
test = "[CSC108H1 / CSC120H1], [MAT137Y1 / MAT157Y1]"


class PrerequisiteTree:
    
    def __init__(self, inp):
        self.logic = ""
        self.groups = []
        self.populate_tree(inp)
        
        
    def populate_tree(self, inp: list):
        if "AND" not in inp:
            self.logic = "OR"
            self.groups = [i for i in inp if i != "OR"]
            return    
        
        andexs = []
        self.logic = "AND"
        while "AND" in inp:
            andex = inp.index("AND")
            andexs.append(andex)
            inp.pop(andex)
        
        andexs.insert(0, 0)
        andexs.append(len(inp) + 1)
        for i in range(len(andexs) - 1):
            self.groups.append(PrerequisiteTree(inp[andexs[i]:andexs[i+1]]))
            
            
    def get_dict(self):
        if self.logic == "AND":
            dih = {
                "logic": self.logic,
                "groups": [i.get_dict() for i in self.groups]
            }
        
        else:
            dih = {
                "logic": self.logic,
                "groups": self.groups
            }
            
        return dih
        


def clean_prereq(inp: str) -> list:
    i = 0
    
    if inp.startswith("<p>"):
        inp = inp[3: len(inp) - 4]
    
    flat = []
    while i < len(inp):
        if inp[i] not in ",/[]()\\;<> " and inp[i:i+3] != "and":
            flat.append(inp[i:i+8])
            i += 8
            continue
            
        elif inp[i] in ";," or inp[i:i+3] == "and":
            flat.append("AND")
            
        elif inp[i] in "/":
            flat.append("OR")         

        i += 1

    return flat


inp = clean_prereq(mat237)
prereqs = PrerequisiteTree(inp)
print(prereqs.get_dict())