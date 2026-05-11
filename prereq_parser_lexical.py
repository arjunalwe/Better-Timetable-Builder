mat237 = "<p>[MAT133Y1/ (MAT130H1/ MAT135H1, MAT136H1)/ (MAT135H5, MAT136H5)/ (MATA30H3/ MATA31H3, MATA36H3), MAT138H1/ MAT102H5/ MAT246H1]/ (MAT148H1, MAT149H1)/ MAT137Y1/ MAT137Y5/ (MAT137H5, MAT139H5)/ (MATA30H3/ MATA31H3, MATA37H3)/ (MAT158H1, MAT159H1)/ MAT157Y1/ MAT157Y5/ (MAT157H5, MAT159H5), MAT223H1/ MATA22H3/ MATA23H3/ MAT240H1/ MAT240H5</p>"
csc111 = "CSC110Y1 (70% or higher)"
eco202 = "(ECO101H1(63%), ECO102H1(63%))/ ECO105Y1(80%)/ ECO100Y5(67%)/ (ECO101H5(63%), ECO102H5(63%))/ (MGEA02H3 (67%), MGEA06H3 (67%)); MAT133Y1/ (MAT130H1/ MAT135H1, MAT136H1)/ (MAT148H1, MAT149H1/ MAT137Y1)/ (MAT158H1, MAT159H1/ MAT157Y1)"
sta272 = "<p>CSC108H1/ CSC110Y1/ CSC148H1, STA220H1/ ECO220Y1/ ECO227Y1/ GGR270H1/ IRW220H1/ PSY201H1/ SOC202H1/ STA261H1/ STA238H1/ STA248H1/ STA288H1/ EEB225H1</p>"
test = "[CSC108H1/ (CSC110Y1, CSC111H1)], [MAT137Y1/ MAT157Y1], STA237H1"


class PrerequisiteTree:
    
    def __init__(self, inp):
        self.logic = ""
        self.groups = []
        self.populate_tree(inp)
        
        
    def populate_tree(self, inp: list):
        if type(inp[0]) is list and len(inp) == 1:
            inp = inp[0]
        
        if "AND" not in inp:
            self.logic = "OR"
            for i in inp:
                if i == "OR":
                    continue
                if type(i) is list:
                    self.groups.append(PrerequisiteTree(i))
                else:
                    self.groups.append(i)
            return

        self.logic = "AND"
        prev = 0
        for i in range(len(inp)):
            if inp[i] == "AND":
                cut = inp[prev:i]
                if len(cut) == 1 and type(cut[0]) is str:
                    self.groups.append(cut[0])
                
                else:
                    self.groups.append(PrerequisiteTree(cut))
                prev = i + 1
        
        cut = inp[prev:]
        if len(cut) == 1 and type(cut[0]) is str:
            self.groups.append(cut[0])
        
        else:
            self.groups.append(PrerequisiteTree(cut))
        
            
            
    def get_dict(self):
        str_groups = []
        for i in self.groups:
            if type(i) is PrerequisiteTree:
                str_groups.append(i.get_dict())
            else:
                str_groups.append(i)
        
        dih = {
                "logic": self.logic,
                "groups": str_groups
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
        
        elif inp[i] in "[(":
            index = inp[i:].find("]") + i if inp[i] == "[" else inp[i:].find(")") + i
            flat.append(clean_prereq(inp[i + 1:index]))      
            i = index
            continue
            
        elif inp[i] in ";," or inp[i:i+3] == "and":
            flat.append("AND")
            if inp[i:i+3] == "and":
                i += 2
            
        elif inp[i] in "/":
            flat.append("OR")

        i += 1

    return flat


inp = clean_prereq(csc111)
prereqs = PrerequisiteTree(inp)
print(prereqs.get_dict())