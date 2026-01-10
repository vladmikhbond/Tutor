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
        return self.splines[0][1] if len(self.splines) > 0 else ""
    
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
        MARKS = ['🔴','🟥','🟦','🟨','🟩','⬛']
        lines = self.source.splitlines()
        for i, l in enumerate(lines):
            if l == "":
                continue
            n = MARKS.find(l[0])
            if n > -1 :
                lines[i] = f"@{n + 1}{l[1:]}"
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
        0 маркує звичайний рядок, 1 маркує {{...}}, 2 маркує [[...]]
        """
        # lexemas   '{{'='\1'     '}}'='\2'     '[['='\3'     ']]'='\4'
        line = line.replace('{{', '\1').replace('}}', '\2').replace('[[', '\3').replace(']]', '\4')
        
        m, s = 0, ""
        res = []
        for c in line:
            if c == '\1':
                res.append((m, s)); s = ""
                m = 1
            elif c == '\2':
                res.append((m, s)); s = ""
                m = 0
            elif c == '\3':
                res.append((m, s)); s = ""
                m = 2
            elif c == '\4':
                res.append((m, s)); s = ""
                m = 0
            else:
                s += c
        res.append((m, s))
        # remove empty lines
        res = [(m, c) for m, c in res if c != ""]
        return res
