import re
from typing import List, Tuple
from .parser import Slide

class RenderHtml:

    def __init__(self, slides: List[Slide], theme: str, lang:str):
        self.slides = slides
        self.theme = theme
        self.lang = lang
        

    def render(self) -> tuple[str, str]:
        lst: List[str] = [] 
        
        for i, slide in enumerate(self.slides):
            if   slide.mark == "@1": x = RenderHtml.render1(slide, i)
            elif slide.mark == "@2": x = RenderHtml.render2(slide, i)
            elif slide.mark == "@3": x = RenderHtml.render3(slide, i)
            elif slide.mark == "@4": x = RenderHtml.render4(slide, i)
            elif slide.mark == "@5": x = RenderHtml.render5(slide, i)
            elif slide.mark == "@6": x = RenderHtml.render6(slide, i)

            lst.append(x)

        body = '\n'.join(lst)
        title = self.slides[0].text

        return (self.html_doc(title, body), title)

    def html_doc(self, title, body):
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
<title>{title}</title>
<link href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css" rel="stylesheet">
<link href='{self.theme}.css' type='text/css' rel='stylesheet' />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.32.2/ace.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.32.2/mode-{self.lang}.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.32.2/theme-{self.theme}.min.js"></script>
</head>
<body>
<div class="container">
{body}
</div>
</body>
</html>
"""
    

    @staticmethod
    def render1(slide: Slide, ord_no: int):
        return f'<div id="n{ord_no}" class="alef1">{slide.text}</div>'
    
    @staticmethod
    def render2(slide: Slide, ord_no: int):
        return f'<div id="n{ord_no}" class="alef2">{slide.text}</div>'
    
    @staticmethod
    def render3(slide: Slide, ord_no: int):
        EN = r"([A-Z,a-z]+)"
        content = ""
        for spot, line in slide.splines:
            # line = html.escape(line)
            # --- plain text: english words italic
            if spot == 0: 
                words = re.split(EN, line)
                for i, w in enumerate(words):
                    if re.match(EN, w):
                        words[i] = (f"<i>{w}</i>")
                content += ''.join(words)
            # --- {{ bold monocpace }}
            elif spot == 1:
                content += f'<span>{line}</span>'
            # --- [[ link|view ]]
            elif spot == 2: 
                if line.startswith("http"):
                    arr = line.split('|')
                    if len(arr) == 1: 
                        content += f'<a href="{line}">{line}</a>'
                    else:
                        content += f'<a href="{arr[0]}">{arr[1]}</a>'
                else:
                    content += f'<img src="pic/{line}" alt="{line}" />'

        return f'<div id="n{ord_no}" class="alef3">{content}</div>'

    @staticmethod
    def render4(slide: Slide, ord_no: int):
        return f'<div id="n{ord_no}" class="alef4">{slide.text}</div>'

    @staticmethod
    def render5(slide: Slide, ord_no: int):
        content = slide.text
        LANG = "python"
        return f'''
<div id="n{ord_no}" class="alef5">
    <div id="editor{ord_no}"></div>
</div>

<script>
    const editor{ord_no} = ace.edit("editor{ord_no}", {{
        theme: "ace/theme/github",
        mode: "ace/mode/{LANG}",
        value:  `{content}`,    
        maxLines: 30,
        wrap: true,
        autoScrollEditorIntoView: true,
    }});
</script>
'''

    @staticmethod
    def render6(slide: Slide, ord_no: int):
        content = '<table><thead>'
        lines = slide.text.strip().splitlines()
        # table header 
        content += '<tr><th>'
        cells = lines[0].split(',')
        cells = [c.strip() for c in cells]
        content += '</th><th>'.join(cells)
        
        content += '</th></hr></thead><tbody>'
        
        # table body
        for line in lines[1:]:
            content += '<tr><td>'
            cells = line.split(',')
            cells = [c.strip() for c in cells]
            content += '</td><td>'.join(cells)
            content += '</td></tr>'

        content += '</tbody></table>'

        return f'<div id="n{ord_no}" class="alef6">{content}</div>'
    






#### тестування рендеру ######
        
# test3([(0, "Hello "), (1, "World"), (0, " !")])
# test3([(0, "Hello "), (2, "https://chatgpt.com/|Чат GPT"), (0, " !")])
# test3([(0, "Я сказав Hello и махнув with foot"),  (0, " !")])

# s = '''
# def test5(t):
#     s = RenderHtml.render5(Slide("@5", t), 42)
#     with open("111.html", "w") as f:
#         f.write(s)
# '''
# test5([(0, s),  (0, " !")])