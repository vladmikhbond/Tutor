import re
from typing import List, Tuple


# int: 0 - plain, 1 - {{plain}}, 2 - [[plain]]
type SpottedLine = Tuple[int, str]

class Slide:
    """
    mark: @1, @2, ...
    splines: [(0, 'abc'), ...]
    text: 'abc' 
    """
    def __init__(self, mark: str, splines: List[SpottedLine]):
        self.mark = mark
        self.splines = splines

    @property
    def text(self):
        return self.splines[0][1]
    
    def __str__(self):
        lst = [str(spline) for spline in self.splines]
        return f"{self.mark}\n{lst}\n"
    

class Parser:
    """
    Результат розбору зберігається в this.slides.
    """
    def __init__(self, source: str):
        self.source = source


    def remove_comments(self):
        lines = self.source.splitlines()
        lines = filter(lambda l: not l.startswith("@@"), lines)
        return "\n".join(lines) 

    def replace_emoji(self):
        MARKS = ['🔴','🔴','📔','❗','📗','📘']
        lines = self.source.splitlines()
        for i, l in enumerate(lines):
            if len(l) > 0 and l[0] in MARKS:
                lines[i] = "@" + l[1:]
        return "\n".join(lines) 


    def parse(self) -> List[Slide]:
        MARK = r"^@[1-6]\s?"
        self.source = self.remove_comments()
        self.source = self.replace_emoji()
        marks = re.findall(MARK, self.source, flags=re.MULTILINE)
        marks = [m.strip() for m in marks]        
        conts = re.split(MARK, self.source, flags=re.MULTILINE)[1:]
        conts = [c.strip() for c in conts]
        slides = [Slide(m, self.line_to_splines(c)) 
                       for m, c in zip(marks, conts)] 
        return slides


    @staticmethod
    def line_to_splines(line: str):
        """
        '111[[222]]333{{4444}}555'  ->  
        [(0, '111'), (2, '222'), (0, '333'), (1, '4444'), (0, '555')]
        """
        T1 = r"\{\{(.*)\}\}"
        T2 = r"\[\[(.*)\]\]"
        
        lst1 = re.split(T1, line)
        lev1 =[(i % 2, s) for i, s in enumerate(lst1) ]

        res: List[SpottedLine] = []
        for m, c in lev1:
            if m == 0:
                lst2 = re.split(T2, c)
                lev2 =[(i % 2 * 2, s) for i, s in enumerate(lst2) ]
                res.extend(lev2)
            else:
                res.append((m, c))
        # clear empty lines
        res = [(m, c) for m, c in res if c != ""]
        return res
