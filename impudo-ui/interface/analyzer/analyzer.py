import lxml.html
from lxml import etree
#import html as html_tools
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
            raise ValueError
        
        try:
            self.elem_tree = lxml.html.parse(url)
        except OSError:
            raise ValueError
            
            
    def _html_text_recursive(self, e):
        if e.tag in ["script", "style"] or not isinstance(e.tag, str):
            return
        if e.tag in self.html_block_elements: yield "\n"
        yield e.text
        for c in e.iterchildren():
            #yield from self._html_text_recursive(c)
            for h in self._html_text_recursive(c):
                yield h
        if e.tag in self.html_block_elements: yield "\n"
        yield e.tail


    def _html_to_text(self, html):
        html = html.replace("\r\n","\n")
        d = lxml.html.document_fromstring(html)
        body = d.xpath('//body')[0]
        text = "".join(filter(None, self._html_text_recursive(body)))
        #text = html_tools.unescape(text)
        text = re.sub("[ \r\t\n\\xa0]+", " ", text).strip()
        text = re.sub("^[  \t\n]+", "", text, flags=re.M).strip()
        return(text)


    def _html_text_recursive_search(self, e):
        if e.tag in ["script", "style"] or not isinstance(e.tag, str):
            return
        if e.tag in self.html_block_elements: yield (e, "\n")
        yield (e, e.text)
        for c in e.iterchildren():
            for h in self._html_text_recursive_search(c):
                yield h
            #yield from self._html_text_recursive_search(c)
        if e.tag in self.html_block_elements: yield (e, "\n")
        yield (e, e.tail)


    def _html_to_text_search(self, html):
        html = html.replace("\r\n","\n")
        d = lxml.html.document_fromstring(html)
        body = d.xpath('//body')[0]
        elements = list(filter(lambda x: x[1] is not None, self._html_text_recursive_search(body)))
        kill_whitespace = False
        text = ""
        text_map = {}
        for e,t in elements:
            t = re.sub("[ \r\t\n\\xa0]+", " ", t)
            if kill_whitespace:          
                t = re.sub("^ +", "", t)
            if not t:
                continue
            kill_whitespace = (t[-1] == " ")
            text_map[len(text)] = e
            text += t.lower()

        return text, text_map, d
    
    
    def _find_path(self, index, text_map, root):
        '''
        Finds an xpath.
        '''
        while text_map.get(index) is None:
            index -= 1
        
        tree = etree.ElementTree(root)
        return tree.getpath(text_map[index])

    """
    def _common(self, path_b, path_e):
        '''
        Copmutes the common part of the path between path_b and path_e.
        '''
        s = difflib.SequenceMatcher(None, path_b, path_e)
        t = s.get_matching_blocks()[0]
        path = path_b[:t.size]
        # if matching stop in '[]' or at '/' the output needs to 
        # be cleaned of open [ or /
        if path[-1] == '[' or '/':
            return path[:path.rfind('/')]
        else:
            return path
    """

    def find_content(self, path):
        '''
        Finds the text referenced by an xpath.
        '''
        result = None
        try:
            result = self.elem_tree.xpath(path)[0]
        except IndexError as e:
            result = self.elem_tree.xpath(path[:path.rfind('/')])[0]
        finally:
            if result is None:
                return ''
            result_html = lxml.etree.tostring(result).decode('utf-8')
            return self._html_to_text(result_html)

    """
    def _find_text(self, text, search_string):
        '''
        Finds matchings between a search_string and a website text.
        '''
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
        '''
        Find all paths that matches where found for.
        '''
        paths = []
        for match in matches:
            # tuple of the beginning of the match and the end of the match so the common path
            # can be computed
            paths.append((self._find_path(match.b, text_map, root), 
                         self._find_path(match.b+match.size, text_map, root)))
        return paths
    """
        
    def _find_paths(self, matches, t_length, text_map, root):
        '''
        Find all paths that matches where found for.
        '''
        paths = []
        sort_m = sorted(matches)
        for k in sort_m:
            v = matches[k]
            k2 = k + len(' '.join(v))
            if k2 > t_length:
                continue
            # tuple of the beginning of the match and the end of the match so the common path
            # can be computed
            for i in range(k, k2+1):
                f = self._find_path(i, text_map, root)
                if f not in paths:
                    paths.append(f)
        d = {}
        for path in paths:
            f = self.find_content(path)
            if not d.get(f, None):
                d[self.find_content(path)] = path
        a_paths = []    
        for v in d.values():
            a_paths.append(v)
            #paths.append((self._find_path(k, text_map, root), 
            #             self._find_path(k2, text_map, root)))
        
        result = []
        for path in paths:
            if path in a_paths:
                result.append(path)
        
        return result
        
    def _find_text(self, text, search_string):
        diff = {}
        i_section = {}
        last_word_diff = False
        i = [1] 
        
        for word in difflib.ndiff(search_string.split(' '), text.split(' ')):
            # check for empty string
            if len(word[2:]) == 0:
                continue
            start_p = word.startswith('+')

            if start_p and last_word_diff:
                for j in i:
                    if not diff.get(j, None):
                        diff[j] = [word[2:]]
                    else:
                        diff[j].append(word[2:])
            elif start_p and not last_word_diff:
                i = [m.start() for m in re.finditer(re.escape(word[2:]), text)]
                #if i == -1:
                #   i = len(text)
                for j in i:
                    if not diff.get(j, None):
                        diff[j] = [word[2:]]
                    else:
                        diff[j].append(word[2:])
                last_word_diff = True
            elif not start_p and last_word_diff:
                i = [m.start() for m in re.finditer(re.escape(word[2:]), text)]
                #if i == -1:
                #    i = len(text)
                for j in i:
                    if not i_section.get(j, None):
                        i_section[j] = [word[2:]]
                    else:
                        i_section[j].append(word[2:])
                last_word_diff = False
            elif not start_p and not last_word_diff:
                for j in i:
                    if not i_section.get(j, None):
                        i_section[j] = [word[2:]]
                    else:
                        i_section[j].append(word[2:])

        return diff, i_section        

    def analyze(self, search_string):
        '''
        Analyzes a websites content to find xpaths that reference the search_string.
        '''
        text, text_map, root = self._html_to_text_search(self.r.text)
        search_string = re.sub("[ \t\n]+", " ", search_string).lower()
        search_string = re.sub("[ \t\n]+$", "", search_string)
        #matches = self._find_text(text, search_string.lower())
        diff, i_section = self._find_text(text, search_string)
        #d_paths = self._find_paths(diff, text_map, root)
        i_paths = self._find_paths(i_section, len(text), text_map, root)
        return i_paths
        '''
        result = []
        for p1,p2 in i_paths:
            path = self._common(p1,p2)
            if not path in result:
                result.append(path)
        '''
        #return result
