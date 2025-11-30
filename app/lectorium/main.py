from typing import List
from .parser import Parser, SpottedLine
from .render_h import RenderHtml 

def translate(source: str, lang: str, theme: str) -> tuple[str, str]:
    """
    Транслює лекцію в HTML
    """
    slides = Parser(source).parse()
    return RenderHtml(slides, lang, theme).render()

    
def get_style(source: str, mark=2) -> List[str]:
    """
    Повертає список рядків, які в лекції стоять в подвійних дужках. 
    """
    slides = Parser(source).parse()
    splines: List[SpottedLine] = []
    for slide in slides:    
        splines.extend(slide.splines)
    lines = [l for (m, l) in splines if m == mark]
    return lines
    
def tune(line: str) -> str:
    """
    Прибирає з рядка символои, не бажані в URL
    """
    forbiddens = " <>\"{}|\\^`[]':/?#[]@!$&'()*+,;="
    lst = ['_' if c in forbiddens else c  for c in line]
    return ''.join(lst);