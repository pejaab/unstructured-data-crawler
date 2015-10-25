import lxml.html
from lxml import etree
#import html as html_tools
import re
import difflib
import requests
import urlparse
import collections

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
        self.check_list = []
           

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
        body = self.elem_tree.xpath('//body')[0]
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

        return text, text_map


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

    def _index(self, parent, child):

        prev = 1
        for i in child.itersiblings(child.tag, preceding=True):
            prev +=1
        return prev

    def _find_all_paths(self, text_map):

        result = []
        tree = etree.ElementTree(self.elem_tree)
        content_path_map = {}
        for _,item in text_map.items():
            path = []
            node = item
            while node.tag != 'html':
                parent = node.getparent()
                idx = self._index(parent, node)
                path.append((node.tag, [node.get('class'), node.get('id'), idx, False]))
                node = parent
            path.reverse()
            content = self.find_content(path)
            if not content_path_map.get(content, None):
                content_path_map[content] = [path]
                result.append((path, content))

        return result
    
    def _find_path(self, text_map, index):
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
        if index in self.check_list:
            return None
        self.check_list.append(index)
        tree = etree.ElementTree(self.elem_tree)
        elem = text_map[index]
        path = []
        while elem.tag != 'html':
            parent = elem.getparent()
            idx = self._index(parent, elem)
            
            path.append((elem.tag, [elem.get('class'), elem.get('id'), idx, False]))
            elem = parent
        path.reverse()
        
        return path


    def find_content(self, path):
        """
        Finds the text referenced by an xpath.

        Args:
            path ():

        Attributes:
            result ():

        Returns:
            
        """
        element = self.search(path[:])
        return self._html_to_text(element)

        
    def _find_paths(self, matches, t_length, text_map):
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
        content_path_map = {}
        result = []
        for k in sort_m:
            v = matches[k]
            k2 = k + len(' '.join(v))
            if k2 > t_length:
                continue
            # tuple of the beginning of the match and the end of the match so the common path
            # can be computed
            for i in range(k, k2+1):
                path = self._find_path(text_map, i)
                if not path:
                    continue
                content = self.find_content(path)
                if not content_path_map.get(content, None):
                    content_path_map[content] = path
                    result.append((path, content))

                #if f not in paths:
                #   paths.append(f)

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

    def analyze(self, search_string=None):
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
        text, text_map = self._html_to_textmap(self.r.text)
        i_paths = []
        if not search_string:
            ordered_text_map = collections.OrderedDict(sorted(text_map.items()))
            i_paths = self._find_all_paths(ordered_text_map)
        else:
            search_string = re.sub("[ \t\n]+", " ", search_string).lower()
            search_string = re.sub("[ \t\n]+$", "", search_string)
            #matches = self._find_text(text, search_string.lower())
            diff, i_section = self._find_text(text, search_string)
            #d_paths = self._find_paths(diff, text_map, root)
            i_paths = self._find_paths(i_section, len(text), text_map)
        return i_paths
        '''
        result = []
        for p1,p2 in i_paths:
            path = self._common(p1,p2)
            if not path in result:
                result.append(path)
        '''
        #return result

        
    def construct_search_path(self, node, path, node_class=None, node_id=None, node_idx=None, modify=False):

        attrib_str = ''
        if node_class:
            attrib_str = '[@class="{0}"]'.format(node_class)
        if node_id:
            attrib_str = '[@id="{0}"]'.format(node_id)
        if node_idx:
            attrib_str += '[{0}]'.format(str(node_idx))

        if path:
            return './/' + node + attrib_str + path[2:]
        return './/' + node + attrib_str

    def search(self, path):
        tree = etree.ElementTree(self.elem_tree)
        
        found = False
        # use class and index as first element often does not have a class
        
        search_str_new = ''
        search_str = ''
        #f =8
        #g = 2
        k = 1
        elements = []
        elements_new = ['']
        #print(path)
        path_old = []
        path[-1][1][3] = True
        if len(path) > 1:
            path[-2][1][3] = True
        while not found:
            for i in range(len(path)-2-k, -1, -4):
                path[i][1][3] = True
            path_old = path[:]
            """
            path_old = path[:]
            node, node_attrib = path.pop()
            node_class, node_id, node_idx, use = node_attrib
            search_str_new = self.construct_search_path(node, search_str, node_class, node_id, node_idx)
            elements_new = tree.findall(search_str_new)
            if len(elements_new) == 1:
                found = True
            if len(path) > 0:
                node, node_attrib = path.pop()
                node_class, node_id, node_idx, use = node_attrib    
                search_str_enw = self.construct_search_path(node, search_str_new, node_class, node_id, node_idx)
                elements_new = tree.findall(search_str_new)
                if len(elements_new) == 1:
                    found = True
            """
            while len(path) > 0 and not found:
                #print(search_str)
                node, node_attrib = path.pop()
                node_class, node_id, node_idx, use = node_attrib
                #f -= 1
                if use:
                    search_str_new = self.construct_search_path(node, search_str, node_class, node_id, node_idx)
                elif not use:
                    search_str_new = self.construct_search_path(node, search_str)
                #elements_new = tree.findall(search_str_new)
                if len(path_old) - len(path) >= k:
                    elements_new = tree.findall(search_str_new)
                    #print(search_str_new)
                    #print(elements_new)
                    #print('#'*20)

                    if len(elements_new) == 1:
                        found = True
                        #print('found')
                        #print('-'*20)
                        break
                    elif len(elements_new) == len(elements):
                        path = path_old[:]
                        path_old = path[:]
                        k += 1
                        elements = elements_new
                        #print('same length')
                        #print('+'*20)
                        break
                    elif len(elements_new) == 0:
                        pass
                    elements = elements_new
                    search_str = search_str_new
                search_str = search_str_new
            search_str = ''
            path = path_old[:]
            #g -= 1    
        return elements_new[0]
    
    def search_to_delete(self, path):
        tree = etree.ElementTree(self.elem_tree)
        
        found = False
        # use class and index as first element often does not have a class
        search_str = ''
        elements = []
        path_new = []
        path, _ = path
        path = path[:]
        min_n = None
        while len(path) > 0 and not found:
            node, node_attrib = path.pop()
            node_class, node_id, node_idx, use = node_attrib
            s_1 = self.construct_search_path(node, search_str, node_class, node_id, node_idx)
            s_2 = self.construct_search_path(node, search_str, node_class, node_idx=node_idx)
            s_3 = self.construct_search_path(node, search_str, node_class, node_id=node_id)
            s_4 = self.construct_search_path(node, search_str, node_id=node_id, node_idx=node_idx)
            s_5 = self.construct_search_path(node, search_str, node_class)
            s_6 = self.construct_search_path(node, search_str, node_id=node_id)
            s_7 = self.construct_search_path(node, search_str, node_idx=node_idx)
            s_8 = self.construct_search_path(node, search_str)
            search_strings = [s_1, s_2, s_3, s_4, s_5, s_6, s_7, s_8]
            for s in search_strings:
                elements = tree.findall(s)
                if len(elements) == 1:
                    found = True
                    break
                if not min_n and len(elements) > 0:
                    min_n = [elements, s]
                else:
                    if len(elements) > 0 and len(elements) < len(min_n[0]):
                        min_n = [elements, s]
            search_str = s
            min_n = None
        
        return self._html_to_text(elements[0])
    
    def eliminate_begin_and_end(self, xpaths, xpath_begin, xpath_end):
        path_begin, content_begin = xpath_begin
        path_end, content_end = xpath_end
        idx_begin = [idx for idx, tup in enumerate(xpaths) if tup[1] == content_begin]
        idx_end = [idx for idx, tup in enumerate(xpaths) if tup[1] == content_end]

        if len(idx_end) != 1:
            content_end = self.search_to_delete(path_end)
            idx_end = [[idx for idx, tup in enumerate(xpaths) if tup[1] == content_end]]
        for i in range(len(xpaths)-1, idx_end[0], -1):
            xpaths.pop()
        if len(idx_begin) != 1:
            content_begin = self.search_to_delete(path_begin)
            idx_begin = [[idx for idx, tup in enumerate(xpaths) if tup[1] == content_begin]] 
        for i in range(idx_begin[0]-1, -1, -1):
            xpaths.pop(i)        

    def eliminate_actives(self, all_paths, actives):
        for tup in actives:
            all_paths.remove(tup)
    
    def eliminate_xpaths(self, stored_xpaths, found_xpaths, xpath_begin, xpath_end):
       
        self.eliminate_begin_and_end(found_xpaths, xpath_begin, xpath_end)

        for path in stored_xpaths:
            try:
                found_xpaths.remove(path)
            except ValueError as _:
                pass

        delete_paths = []
        for path in found_xpaths:
            new_path = path
            while new_path:
                new_path = new_path[:new_path.rfind('/')]
                if new_path in found_xpaths:
                    delete_paths.append(path)
        
        for path in delete_paths:
            try:
                found_xpaths.remove(path)
            except ValueError as _:
                pass
        
        return found_xpaths
