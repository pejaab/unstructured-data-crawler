from __future__ import division
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
import hashlib
import os
#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Analyzer(object) :

    html_block_elements = {
        "article", "blockquote", "dd", "div", "dl", "fieldset", "figcaption",
        "figure", "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6", "header",
        "hgroup", "hr", "li", "noscript", "ol", "output", "p", "pre", "section", "table",
        "tr", "th", "td", "tfoot", "thead", "ul", "br",
        }

    words_to_remove = ['png', 'gif', 'logo', 'facebook', 'pinterest', 'linkedin']

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
            'User-agent': 'python-requests/2.8.1'
        }
        self.url = url
        self.r = requests.get(url=url, headers=headers)
        self.r.raise_for_status()
        self.elem_tree = lxml.html.document_fromstring(self.r.content).xpath('//body')[0]
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


    def _html_to_textmap(self):
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

        elements = list(filter(lambda x: x[1] is not None, self._html_textmap_recursive(self.elem_tree)))
        kill_whitespace = False
        text = ""
        text_map = {}
        for e,t in elements:
            t = re.sub("[ \r\t\n\\xa0]+", " ", t)
            t = re.sub("^ +", "", t)
            t = re.sub(" +$", "", t)
            if not t:
                continue
            text_map[len(text)] = e
            text += t.lower() + " "

        return text[:-1], text_map


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
        if e.tag == 'img':
            url = e.get('src')
            if url is not None:
                if 'http' in url:
                    for word in self.words_to_remove:
                        if word in url.lower():
                            return
                    size = self._get_img_size(url)
                    if size:
                        yield (e, url, size)
        for c in e.iterchildren():
            for h in self._html_img_recursive(c):
                yield h

    def _html_to_img(self):

        elements = list(self._html_img_recursive(self.elem_tree))
        return elements

    def _find_img(self, url):
        url = url.encode('utf-8')
        url = urllib.quote(urllib.unquote(url[url.rfind('/')+1:]))
        elements = self._html_to_img()
        element = next(((elem, u) for elem, u in elements if u[u.rfind('/')+1:] == url), None)

        return element[0]

    def find_img_url(self, url):
        return self._find_img(url).get('src')

    def _find_all_paths(self, text_map):

        result = []
        tree = etree.ElementTree(self.elem_tree)
        content_path_map = {}
        for _,item in text_map.items():
            path = []
            node = item
            while node.tag != 'body':
                parent = node.getparent()
                path.append((node.tag, [node.get('class'), node.get('itemprop'), node.get('id')]))
                node = parent
            path.append(('body', [None, None, None]))
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
        while elem.tag != 'body':
            parent = elem.getparent()

            path.append((elem.tag, [elem.get('class'), elem.get('itemprop'), elem.get('id')]))
            elem = parent
        path.append(('body', [None, None, None]))

        return path

    def _find_img_path(self, elem, num_to_forget):

        tree = etree.ElementTree(self.elem_tree)
        path = []
        while elem.tag != 'html':
            parent = elem.getparent()
            if num_to_forget <= 0:
                path.append((elem.tag, [elem.get('class'), elem.get('itemprop'), elem.get('id')]))
            elem = parent
            num_to_forget -= 1

        return path

    def _find_descendant_imgs(self, elem):
        if not isinstance(elem.tag, str):
            return
        if elem.tag == 'img':
            url = elem.get('src')
            if 'http' in url:
                for word in self.words_to_remove:
                    if word in url.lower():
                        return
                yield url
        for e in elem.iterchildren():
            for h in self._find_descendant_imgs(e):
                yield h

    def _get_img_size(self, img):
        response = requests.get(img)
        try:
            img_child = Image.open(StringIO(response.content))
        except IOError:
            return None
        return img_child.size

    def download_img(self, img):
        response = requests.get(img)
        name = urllib.unquote(img)
        name = hashlib.sha1(name).hexdigest()
        path = os.path.join(os.path.dirname(BASE_DIR), 'media', 'thumbnail')
        try:
            img = Image.open(StringIO(response.content))
        except IOError:
            return None
        img.save(path + '/' + name, 'jpeg')
        return 'thumbnail/' + name

    def search_imgs(self, path):

        tree = etree.ElementTree(self.elem_tree)
        search_term = []
        while len(path) > 0:
            node, node_attrib = path.pop()
            node_class, node_item, node_id = node_attrib
            node_class_new = None
            if node_class:
                search_str = self.attrib_contains(node, node_class, 'class')
            elif not node_class and node_item:
                search_str = self.attrib_contains(node, node_item, 'itemprop')
            elif not node_class and not node_item and node_id:
                search_str = self.attrib_contains(node, node_id, 'id')
            else:
                search_str = "//{}".format(node)
            search_term.append(search_str)
        search_term = ''.join(search_term)
        elements = tree.xpath(search_term)
        result = []
        for elem in elements:
            imgs = list(self._find_descendant_imgs(elem))
            if imgs:
                result += imgs
        return result

    def _does_not_belong(self, img):
        _, u, s = img
        keep = False
        width, height = s
        if width / height <= 1/2 or width / height >= 2/1:
            return False
        return True

    def _remove_imgs(self, imgs):
        result = []
        for img in imgs:
            keep = self._does_not_belong(img)
            if keep:
                result.append(img)
        return result

    def _find_roots(self, paths):
        reduced_paths = collections.OrderedDict()
        if len(paths) > 20:
            paths = paths[:20]
        for p,e in paths:
            p_copy = p[:]
            p_copy = p_copy.split('/')
            j = 0
            while True:
                p_copy.pop()
                j += 1
                if len(p_copy) == 0:
                    break
                if 'li' in p_copy[-1]:
                    p_copy.pop()
                    j += 1
                    break
                if 'div' in p_copy[-1]:
                    break
            if len(p_copy) == 0:
                continue
            p_copy = ('/').join(p_copy)
            if reduced_paths.get(p_copy) is None:
                reduced_paths[p_copy] = (e,j)

        return reduced_paths

    def analyze_img(self):
        imgs = self._html_to_img()
        imgs = self._remove_imgs(imgs)
        paths = []
        result = []
        tree = etree.ElementTree(self.elem_tree)
        for e,_,_ in imgs:
            path = tree.getelementpath(e)
            paths.append((path, e))
        if len(paths) == 1:
            roots = collections.OrderedDict()
            roots[paths[0][0]] = (paths[0][1], 0)
        elif len(paths) > 1:
            roots = self._find_roots(paths)
        for path, elem in roots.items():
            e, num = elem
            p = self._find_img_path(e, num)
            if p and p not in result:
                result.append(p)

        reduced_paths = []
        for path in result:
            reduced_paths.append(self.search_imgs(path[:]))
        if len(reduced_paths) >= 2 and len(reduced_paths[0]) == 1:
            main_img_name = reduced_paths[0][0].split('/')[-1]

            # check if main image is contained in the succeeding image gallery
            if main_img_name == reduced_paths[1][0].split('/')[-1]:
                result = result[1:]

        return result

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
        if elements is None:
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
        text, text_map = self._html_to_textmap()
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

    def attrib_contains(self, node, attrib, attrib_name):
        match = re.search(r'[-|_](\d+)|id(\d+[\d\w]+).*', attrib)
        article_id = match.group() if match else None
        if article_id:
            attrib = attrib[:attrib.index(article_id)]
        attrib = re.sub("[ \t\n]+", " ", attrib)
        attrib = re.sub("[ \t\n]+$", "", attrib)
        search_str = "//{}[contains(concat(' ', normalize-space(@{}), ' '), '{}')]".format(node, attrib_name, attrib)
        return search_str

    def search(self, path):

        tree = etree.ElementTree(self.elem_tree)
        search_term = []
        while len(path) > 0:
            node, node_attrib = path.pop()
            node_class, node_item, node_id = node_attrib
            node_class_new = None
            if node_class:
                search_str = self.attrib_contains(node, node_class, 'class')
            elif not node_class and node_item:
                search_str = self.attrib_contains(node, node_item, 'itemprop')
            elif not node_class and not node_item and node_id:
                search_str = self.attrib_contains(node, node_id, 'id')
            else:
                search_str = "//{0}".format(node)
            search_term.append(search_str)

        search_term = ''.join(search_term)
        elements = tree.xpath(search_term)
        if len(elements) < 1:
            return None
        return elements
