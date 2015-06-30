import lxml.html as lh
from lxml.etree import tostring
#from dao import Dao

class Analyzer(object) :

   xpath = "//*[contains(normalize-space(.), '{0}') and not(.//*[contains(normalize-space(.), '{0}')])]/*"

   @classmethod
   def search_path(self, url, input_string) :
       elem_tree = lh.parse(url)
       node = elem_tree.xpath(self.xpath.format(input_string))[0]
       path = elem_tree.getpath(node)
       #Use parent path
       path = path[:path.rfind('/')]
       # #Css selector
       # result = elem_tree.xpath(path)[0]
       # result_class = result.attrib.get('class')
       return path

   @classmethod
   def search_content(self, url, path):
       elem_tree = lh.parse(url)
       result = elem_tree.xpath(path)[0]
       result_html = tostring(result).decode('utf-8')
       return result_html
    
   
   @staticmethod
   def find_path() :
       html_file = "ETOZGianfranco.html"
       input_string = "Gianfranco Frattini"
       elem_tree = lh.parse(html_file)
       xpath = "//*[contains(normalize-space(.), '{0}') and not(.//*[contains(normalize-space(.), '{0}')])]/*"
       node = elem_tree.xpath(xpath.format(input_string))[0]
       path = elem_tree.getpath(node)
       #Use parent path
       path = path[:path.rfind('/')]
       #Use template
       result = elem_tree.xpath(path)[0]
       result_html = tostring(result)
       result_class = result.attrib.get('class')
       print('{0} -> {1}'.format(input_string, elem_tree.getpath(node)))
       #Use template
       html_file2 = "ETOZCocktail.html"
       elem_tree2 = lh.parse(html_file2)
       result2 = elem_tree2.xpath(path)[0]
       result2_html = tostring(result2)
       #Create dao
       dao = Dao()
       #Update template
       dao.update_path(19, path)
       #Insert record
       dao.insert_record('TestUrl', result_html, 19)
       dao.insert_record('TestUrl', result2_html, 19)
   
Analyzer.find_path()
path = Analyzer.search_path('http://www.etoz.ch/kyoto/', 'Gianfranco Frattini')
Analyzer.search_content('http://www.etoz.ch/ospite/', path)
