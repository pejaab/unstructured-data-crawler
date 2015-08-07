import lxml.html
from lxml import etree
import html as html_tools
import re
import difflib
import requests

class Analyzer(object) :

    html_block_elements = {
        "article", "blockquote", "dd", "div", "dl", "fieldset", "figcaption",
        "figure", "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6", "header",
        "hgroup", "hr", "li", "noscript", "ol", "output", "p", "pre", "section", "table",
        "tr", "th", "td", "tfoot", "thead", "ul", "br",
        }

    def __init__(self, url):
        self.r = requests.get(url)
        try:
            self.r.raise_for_status()
        except requests.HTTPError as e:
            pass
        self.elem_tree = lxml.html.parse(url)
        
    def _html_text_recursive(self, e):
        if e.tag in ["script", "style"] or not isinstance(e.tag, str):
            return
        if e.tag in self.html_block_elements: yield "\n"
        #if e.tag == "li": yield "• "
        yield e.text
        for c in e.iterchildren():
            yield from self._html_text_recursive(c)
        if e.tag in self.html_block_elements: yield "\n"
        yield e.tail


    def _html_to_text(self, html):
        html = html.replace("\r\n","\n")
        d = lxml.html.document_fromstring(html)
        body = d.xpath('//body')[0]
        text = "".join(filter(None, self._html_text_recursive(body)))
        text = html_tools.unescape(text)
        text = re.sub("[ \t\n]+", " ", text).strip()
        text = re.sub("^[  \t\n]+", "", text, flags=re.M).strip()
        return(text)


    def _html_text_recursive_search(self, e):
        if e.tag in ["script", "style"] or not isinstance(e.tag, str):
            return
        if e.tag in self.html_block_elements: yield (e, "\n")
        #if e.tag == "li": yield "• "
        yield (e, e.text)
        for c in e.iterchildren():
            yield from self._html_text_recursive_search(c)
        if e.tag in self.html_block_elements: yield (e, "\n")
        yield (e, e.tail)


    def _html_to_text_search(self, html):
        html = html.replace("\r\n","\n")
        html = html.replace('\xa0', ' ')
        d = lxml.html.document_fromstring(html)
        body = d.xpath('//body')[0]
        elements = list(filter(lambda x: x[1] is not None, self._html_text_recursive_search(body)))
        kill_whitespace = False
        text = ""
        text_map = {}
        for e,t in elements:
            t = re.sub("[ \t\n]+", " ", t)
            if kill_whitespace:          
                t = re.sub("^ +", "", t)
            if not t:
                continue
            kill_whitespace = (t[-1] == " ")
            text_map[len(text)] = e
            text += t.lower()

        return text, text_map, d
    
    
    def _find_path(self, index, text_map, root):
        while text_map.get(index) is None:
            index -= 1

        tree = etree.ElementTree(root)
        return tree.getpath(text_map[index])


    def _common(self, path_b, path_e):
        s = difflib.SequenceMatcher(None, path_b, path_e)
        t = s.get_matching_blocks()[0]
        path = path_b[:t.size]
        # if matching stop in '[]' or at '/' the output needs to 
        # be cleaned of open [ or /
        if path[-1] == '[' or '/':
            return path[:path.rfind('/')]
        else:
            return path


    def find_content(self, path):
        try:
            result = self.elem_tree.xpath(path)[0]
        except IndexError as e:
            result = self.elem_tree.xpath(path[:path.rfind('/')])[0]
        finally:
            result_html = lxml.etree.tostring(result).decode('utf-8')
            return self._html_to_text(result_html)


    def _find_text(self, text, search_string):
        s = difflib.SequenceMatcher(None, search_string, text)
        m = s.get_matching_blocks()
        m2 = m
        m3 = m
        while len(m) == len(m2):
            l = m2[0].b + m2[0].size
            t = ' ' * (l) + text[l:]
            s.set_seq2(t)
            m2 = s.get_matching_blocks()
            m3 += m2
        return set(m3)


    def _find_paths(self, matches, text_map, root):
        paths = []
        for match in matches:
            paths.append((self._find_path(match.b, text_map, root), 
                         self._find_path(match.b+match.size, text_map, root)))

        return paths
    
    def analyze(self,  search_string):
        text, text_map, root = self._html_to_text_search(self.r.text)
        search_string = re.sub("[ \t\n]+", " ", search_string)
        matches = self._find_text(text, search_string.lower())

        paths = self._find_paths(matches, text_map, root)

        result = []
        for p1,p2 in paths:
            path = self._common(p1,p2)
            if not path in result:
                result.append(path)

        return result
