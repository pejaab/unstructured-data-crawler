import lxml.html
from lxml import etree
#import html as html_tools
import re
import difflib
import requests
import urlparse
import urllib
import collections
from PIL import Image
from StringIO import StringIO

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
        headers = {
            'User-agent': 'Mozilla/5.0'
        }
        self.url = url
        self.r = requests.get(url=url, headers=headers)
        self.r.raise_for_status()
        self.elem_tree = lxml.html.document_fromstring(self.r.text)
        self.elem_tree.make_links_absolute(url)
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
        if e.tag == 'img': yield (e, e.get('src').encode('utf-8'))
        for c in e.getchildren(): #e.iterchildren():
            for h in self._html_img_recursive(c):
                yield h

    def _html_to_img(self):

        body = self.elem_tree.xpath('//body')[0]
        elements = list(self._html_img_recursive(body))
        return elements

    def _find_img(self, url):
        url = url.encode('utf-8')
        url = urllib.quote(urllib.unquote(url[url.rfind('/')+1:]))
        elements = self._html_to_img()
        element = next(((elem, u) for elem, u in elements if urllib.quote(u[u.rfind('/')+1:]) == url), None)

        return element[0]

    def find_img_url(self, url):
        return self._find_img(url).get('src')

    def _index(self, parent, child):

        same = 1
        for i in child.iter(child.tag):
            same += 1

        if same > 1:

            prev = 1
            for i in child.itersiblings(child.tag, preceding=True):
                prev += 1
            return prev
        else:
            prev = 1
            for i in child.itersiblings(preceding=True):
                prev += 1
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
                path.append((node.tag, [node.get('class'), node.get('itemprop'), node.get('id'), idx]))
                node = parent
            content = self.find_content(path)
            if not content:
                continue
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

            path.append((elem.tag, [elem.get('class'), elem.get('itemprop'), elem.get('id'), idx]))
            elem = parent

        return path

    def _find_img_path(self, elem):

        tree = etree.ElementTree(self.elem_tree)
        path = []
        while elem.tag != 'html':
            parent = elem.getparent()
            idx = self._index(parent, elem)

            path.append((elem.tag, [elem.get('class'), elem.get('itemprop'), elem.get('id'), idx]))
            elem = parent

        return path

    def _find_descendant_imgs(self, elem):
        if not isinstance(elem.tag, str):
            return
        if elem.tag == 'img':
            url = elem.get('src')
            if url is not None:
                yield url
        for e in elem.iterchildren():
            for h in self._find_descendant_imgs(e):
                if h is not None:
                    yield h

    def _get_img_size(self, img):
        response = requests.get(img)
        img_child = Image.open(StringIO(response.content))
        return img_child.size

    def search_imgs(self, path):

        tree = etree.ElementTree(self.elem_tree)
        search_term = []
        while len(path) > 0:
            node, node_attrib = path.pop()
            node_class, node_item, node_id, node_idx = node_attrib
            node_class_new = None
            if node_class:
                search_str = self.class_contains(node, node_class)
            elif not node_class and node_item:
                search_str = "//{0}[contains(concat(' ', normalize-space(@itemprop), ' '), '{1}')]".format(node, node_item)
            elif not node_class and not node_item and node_id:
                search_str = "//{0}[contains(concat(' ', normalize-space(@id), ' '), '{1}')]".format(node, node_id)
            else:
                search_str = "//{0}".format(node)
            search_term.append(search_str)
        search_term = ''.join(search_term)

        elements = tree.xpath(search_term)

        return list(self._find_descendant_imgs(elements[0]))

    def analyze_img(self, link):
        elem = self._find_img(link)
        elem = elem.getparent() # to loose img elem
        elem = elem.getparent() # to access img from first top level

        imgs = list(self._find_descendant_imgs(elem))
        width, height = self._get_img_size(imgs[0])
        elem_new = elem
        imgs_new = []
        result_elems = []
        for _ in range(0, 2):
            elem_new = elem_new.getparent()
            imgs_new = list(self._find_descendant_imgs(elem_new))
            if len(imgs_new) > len(imgs):
                children = list(elem_new)
                for child in children:
                    imgs_child = list(self._find_descendant_imgs(child))
                    if len(imgs_child) == 0:
                        continue
                    width_child, height_child = self._get_img_size(imgs_child[0])
                    if width > width_child or height > height_child:
                        pass
                    else:
                        result_elems.append(child)
                break

        if len(imgs_new) > len(imgs):
            elems = result_elems
        else:
            children = list(elem)
            for child in children:
                imgs_child = list(self._find_descendant_imgs(child))
                if len(imgs_child) == 0:
                    continue
                width_child, height_child = self._get_img_size(imgs_child[0])
                if width > width_child or height > height_child:
                    pass
                else:
                    result_elems.append(child)
            elems = result_elems

        paths = []
        for elem in elems:
            paths.append(self._find_img_path(elem))

        return paths

    def find_content(self, path):
        """
        Finds the text referenced by an xpath.

        Args:
            path ():

        Attributes:
            result ():

        Returns:

        """
        elements = self.search(path[:])
        result = ''
        if not elements:
            return None
        for elem in elements:
            result += '\n' + self._html_to_text(elem)
        return result

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
                if not content:
                    continue
                if not content_path_map.get(content, None):
                    content_path_map[content] = path
                    result.append((path, content))

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
                for j in i:
                    if not diff.get(j, None):
                        diff[j] = [word[2:]]
                    else:
                        diff[j].append(word[2:])
                last_word_diff = True
            elif not start_p and last_word_diff:
                i = [m.start() for m in re.finditer(re.escape(word[2:]), text)]
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
            diff, i_section = self._find_text(text, search_string)
            i_paths = self._find_paths(i_section, len(text), text_map)
        return i_paths

    def eliminate_begin_and_end(self, xpaths, xpath_begin, xpath_end):
        path_begin, content_begin = xpath_begin
        path_end, content_end = xpath_end
        idx_begin = [idx for idx, tup in enumerate(xpaths) if tup[1] == content_begin]
        idx_end = [idx for idx, tup in enumerate(xpaths) if tup[1] == content_end]
        if len(idx_end) != 1:
            content_end = self._html_to_text(self.search(path_end[:])[0])
            idx_end = [idx for idx, tup in enumerate(xpaths) if tup[1] == content_end]
            if len(idx_end) == 0:
                return False
        for i in range(len(xpaths)-1, idx_end[0]-1, -1):
            xpaths.pop()
        if len(idx_begin) != 1:
            content_begin = self._html_to_text(self.search(path_begin[:])[0])
            idx_begin = [idx for idx, tup in enumerate(xpaths) if tup[1] == content_begin]
            if len(idx_begin) == 0:
                return False
        for i in range(idx_begin[0], -1, -1):
            xpaths.pop(i)

        return True


    def eliminate_actives(self, all_paths, actives):
        """
        After saving active records as actives, they are deleted from pool, so not to save them twice.
        """
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


    def class_contains(self, node, class_name):

        #match = re.search(r'(id-|post-)(\d+).*', class_name)
        match = re.search(r'(-|_)(\d+).*', class_name)
        article_id = match.group(2) if match else None
        if article_id:
            class_name = class_name[:class_name.index(article_id)]
        class_name = re.sub("[ \t\n]+", " ", class_name)
        class_name = re.sub("[ \t\n]+$", "", class_name)
        search_str = "//{0}[contains(concat(' ', normalize-space(@class), ' '), '{1}')]".format(node, class_name)
        return search_str

    def search(self, path):

        tree = etree.ElementTree(self.elem_tree)
        search_term = []
        while len(path) > 0:
            node, node_attrib = path.pop()
            node_class, node_item, node_id, node_idx = node_attrib
            node_class_new = None
            if node_class:
                search_str = self.class_contains(node, node_class)
            elif not node_class and node_item:
                search_str = "//{0}[contains(concat(' ', normalize-space(@itemprop), ' '), '{1}')]".format(node, node_item)
            elif not node_class and not node_item and node_id:
                search_str = "//{0}[contains(concat(' ', normalize-space(@id), ' '), '{1}')]".format(node, node_id)
            else:
                search_str = "//{0}".format(node)
            search_term.append(search_str)

        search_term = ''.join(search_term)

        elements = tree.xpath(search_term)
        if len(elements) == 1:
            return elements
        elif len(elements) > 1:
            parent = elements[0].getparent()
            return parent
        else:
            return None
