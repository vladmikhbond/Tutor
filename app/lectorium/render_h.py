import re
from typing import List, Tuple
from .parser import Slide

class RenderHtml:

    def __init__(self, slides: List[Slide], lang:str, theme: str):
        self.slides = slides
        self.lang = lang
        self.theme = theme
        #TODO:  коли бу схеми ace9, поставити їх 
        self.ace_theme = "monokai" if theme.endswith("_dark") else "github" 

    def render(self) -> tuple[str, str]:
        lst: List[str] = [] 
        
        for i, slide in enumerate(self.slides):
            if   slide.mark == "@1": x = self.render1(slide, i)
            elif slide.mark == "@2": x = self.render2(slide, i)
            elif slide.mark == "@3": x = self.render3(slide, i)
            elif slide.mark == "@4": x = self.render4(slide, i)
            elif slide.mark == "@5": x = self.render5(slide, i)
            elif slide.mark == "@6": x = self.render6(slide, i)

            lst.append(x)

        content = '\n'.join(lst)
        title = self.slides[0].text

        return self.html_doc(content)
    

    def html_doc(self, content):
        """
           Кінцева html сторінка.
           Обирає світлу або темну тему редактора ace9.
        """
        title = self.slides[0].text
         
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
<title>{title}</title>
<link href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css" rel="stylesheet">
<link href='sys/engine.css' type='text/css' rel='stylesheet' />
<link id="theme_link" href='sys/themes/{self.theme}.css' type='text/css' rel='stylesheet' />

<script src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.32.2/ace.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.32.2/mode-{self.lang}.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.32.2/theme-{self.ace_theme}.min.js"></script>

<script>
    const START_SLIDE_NO={0}; 
    const VERSION = "tutor";
</script>


</head>
<body>
    <div class="container">
        <div id="dash" > 
            <a href="#" id="theme_toggle"> ◐ </a>
            <a href="#" id="pensil"> ✏ </a>
        </div>
        <div id="lecture">
            {content}
        </div>
        <script src='sys/engine.js'></script>
    </div>
</body>
</html>
"""
    
    def render1(self, slide: Slide, ord_no: int):
        return f'<div id="n{ord_no}" class="alef1">{slide.text}</div>'
    
    def render2(self, slide: Slide, ord_no: int):
        return f'<div id="n{ord_no}" class="alef2">{slide.text}</div>'
    
    def render3(self, slide: Slide, ord_no: int):
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


    def render4(self, slide: Slide, ord_no: int):
        return f'<div id="n{ord_no}" class="alef4">{slide.text}</div>'


    def render5(self, slide: Slide, ord_no: int):
        content = slide.text
        return f'''
<div id="n{ord_no}" class="alef5">
    <div id="editor{ord_no}"></div>
</div>

<script>
    const editor{ord_no} = ace.edit("editor{ord_no}", {{
        theme: "ace/theme/{self.ace_theme}",
        mode: "ace/mode/{self.lang}",
        value:  `{content}`,    
        maxLines: 30,
        wrap: true,
        autoScrollEditorIntoView: true,
    }});
    editor{ord_no}.session.setUseWorker(false);
</script>
'''

    def render6(self, slide: Slide, ord_no: int):
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
    






