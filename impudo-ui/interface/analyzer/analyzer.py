import lxml.html
from lxml import etree
#import html as html_tools
import re
import difflib
import requests
import urlparse

class Analyzer(object) :

    html_block_elements = {
        "article", "blockquote", "dd", "div", "dl", "fieldset", "figcaption",
        "figure", "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6", "header",
        "hgroup", "hr", "li", "noscript", "ol", "output", "p", "pre", "section", "table",
        "tr", "th", "td", "tfoot", "thead", "ul", "br",
        }

    def __init__(self, url):
        """
        Preloads the url and parses it into an element tree.

        Args:
            url (str): e.g. http://www.etoz.ch.model-2145.

        Attributes:
            url (str): Represents url.
            r (requests.models.Response): Response fetched from url.
            elem_tree (lxml.etree._ElementTree): Parsed element tree from url.
        """
        self.url = url
        self.r = requests.get(url)
        self.r.raise_for_status()
        self.elem_tree = lxml.html.document_fromstring(self.r.text)
           

    def _html_text_recursive(self, e):
        """
        Generates the text of an element.

        Args:
            e (lxml.html.HtmlElement): HtmlElement of an element tree.

        Yields:
            str: The text of the next element or a new line.
        """
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


    def _html_to_text(self, body):
        """
        Generates the text of a website by cleaning the html tags.

        Args:
            body (str): string representation of HTML document.

        Attributes:
            text (str): cleand string representation of HTML document

        Returns:
            str: Cleaned text of website
        """

        text = "".join(filter(None, self._html_text_recursive(body)))
        #text = html_tools.unescape(text)
        text = re.sub("[ \r\t\n\\xa0]+", " ", text).strip()
        text = re.sub("^[  \t\n]+", "", text, flags=re.M).strip()
        return text


    def _html_textmap_recursive(self, e):
        """
        Generates a mapping between element and the text of the corresponding element.

        Args:
            e (lxml.html.HtmlElement): HtmlElement of an element tree.

        Yields:
            (lxml.html.HtmlElement, str): The element plus the text corresponding to the element or a new line.
        """

        if e.tag in ["script", "style"] or not isinstance(e.tag, str):
            return
        if e.tag in self.html_block_elements: yield (e, "\n")
        yield (e, e.text)
        for c in e.iterchildren():
            for h in self._html_textmap_recursive(c):
                yield h
            #yield from self._html_textmap_recursive(c)
        if e.tag in self.html_block_elements: yield (e, "\n")
        yield (e, e.tail)


    def _html_to_textmap(self, html):
        #TODO: documentation
        """
        Generates the text of a website by cleaning the html tags and a mapping between element and text.

        Args:
            html (str): string representation of HTML document.

        Attributes:
            d (lxml.html.HtmlElement): HTML document
            body (lxml.html.HtmlElement): HTML document containing only body
            elements (): 
            kill_whitespace (boolean): 
            text (str): cleand string representation of HTML document
            text_map ():

        Returns:
            str: Cleaned text of website
        """

        html = html.replace("\r\n","\n")
        d = lxml.html.document_fromstring(html)
        body = d.xpath('//body')[0]
        elements = list(filter(lambda x: x[1] is not None, self._html_textmap_recursive(body)))
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

    def _html_img_recursive(self, e): 
        """
        Generates the text of elements.

        Args:
            e (lxml.html.HtmlElement): HtmlElement of an element tree.

        Yields:
            str: The text of the next element or a new line.
        """
        if e.tag in ["script", "style"] or not isinstance(e.tag, str):
            return
        if e.tag == 'img': yield (e, e.attrib)
        #TODO: if nothing is returned then turn of this condition
        #if e.tag == "a": # thumbnails usually are below 'a' and are not needed
            #return
        for c in e.iterchildren():
            for h in self._html_img_recursive(c):
                yield h

    def _html_to_img(self):

        body = self.elem_tree.xpath('//body')[0]
        elements = self._html_img_recursive(body)
        return elements, body

    def _find_img_urls(self, elements, url, url_extended):
        result = []
        for elem,attr in elements:
            if elem.tag == "img":
                l = attr.get('src', None)
            #elif elem.tag == "a":
                #l = attr.get('href', None)
            if l is None:
                continue
            l = urlparse.urljoin(url, l)
            l = l[:l.rfind('/')] + '/'
            if url_extended == l[:l.rfind('/')] + '/':
                result.append((elem, attr['src'].replace(' ', '%20')))
        return result  
    
    def _find_imgs(self, xpath, link):
        elements, _ = self._html_to_img()
        elements = list(elements)
        result = []
        if xpath:
            link = self.find_img_url(xpath)

        url_base = urlparse.urlparse(self.url)
        url_base = url_base.scheme + '://' + url_base.netloc
        url_extended = urlparse.urljoin(url_base, link)
        url_extended = url_extended[:url_extended.rfind('/')] + '/'
        result = self._find_img_urls(elements, url_extended, url_extended)
        if not result:
            result = self._find_img_urls(elements, url_base, url_extended)
        
        return result
    
    def find_img_xpath(self, link):
        urls = self._find_imgs(None, link)
        tree = etree.ElementTree(self.elem_tree)
        for elem, url in urls:
            if url == link:
                return tree.getpath(elem)
            
    def find_img_url(self, path):
        path += '/@src'
        result = self.elem_tree.xpath(path)[0]
        return result.replace(' ', '%20')

    def _url_exists(self, url):
        r = requests.get(url)
        return (r.status_code == 200)
   
    
    def find_imgs(self, xpath):
        elements = self._find_imgs(xpath, None)
        url_base = urlparse.urlparse(self.url)
        url_base = url_base.scheme + '://' + url_base.netloc
        result = []
        for e, url in elements:
            u = urlparse.urljoin(url_base, url)
            if self._url_exists(u):
                result.append(u)
        return result

    
    def _find_path(self, index, text_map, root):
        """
        Finds an xpath corresponding to the closest entry in a mapping between index and element.

        Args:
            index (int):
            text_map ():
            root ():

        Attributes:
            tree

        Returns:
            
        """
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
        """
        Finds the text referenced by an xpath.

        Args:
            path ():

        Attributes:
            result ():

        Returns:
            
        """
        result = None
        try:
            result = self.elem_tree.xpath(path)[0]
        except IndexError as e:
            result = self.elem_tree.xpath(path[:path.rfind('/')])[0]
        finally:
            if result is None:
                return ''
            return self._html_to_text(result)

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

        Args:
            matches ():
            t_length ():
            text_map ():
            root ():

        Attributes:
            paths ():
            sort_m ():
            v ():
            k2 ():
            f ():
            d ():
            a_paths ():
            result ():

        Returns:
            
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
        """
        

        Args:
            text ():
            search_string ():

        Attributes:
            diff ():
            i_section ():
            last_word_diff (boolean):
            start_p (boolean):

        Returns:
            
        """
        
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
        """
        Analyzes a websites content to find xpaths that reference the search_string.

        Args:
            search_string ():

        Attributes:
            text ():
            text_map ():
            root ():
            diff ():
            i_section ():
            i_paths ():
        """
        text, text_map, root = self._html_to_textmap(self.r.text)
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
