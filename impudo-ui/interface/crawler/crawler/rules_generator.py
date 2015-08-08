import difflib
from difflib import SequenceMatcher
from dao import Dao

def remove_host(url, domain):
	return url[url.find(domain)+len(domain):]

def longest_match(urls):
	result = urls[0]
	length = len(urls)
	for index in range(length-1):
		s = SequenceMatcher(None, result, urls[index+1])
		i, j, k = s.find_longest_match(0,len(result),0,len(urls[index+1]))
		result = result[i:i+k]

	return result

def generate_rule(urls, domain):
	return remove_host(longest_match(urls),domain)

def save_rules(urls, domain):
	d = Dao()
	
	follow_rules=""
	parse_rules = generate_rule(TestUrls,domain)
	follow_rules_deny = ""
	parse_rules_deny = ""

	#insert only if no previous entry exists
	if not d.get_rules(domain):
		d.insert_rule(domain,follow_rules,parse_rules,follow_rules_deny,parse_rules_deny)



if __name__ == "__main__":

	domain = "vittorioragone.com"

	TestUrls = [ "http://www.vittorioragone.com/stock/product.php?p=491?img=0",
		"http://www.vittorioragone.com/stock/product.php?p=501?img=0",
		"http://www.vittorioragone.com/stock/product.php?p=654?img=0",
		"http://www.vittorioragone.com/stock/product.php?p=123?img=0"
	]

	domain2 = "etoz.ch"
	TestUrls2 = ["http://www.etoz.ch/la-tourette/",
		"http://www.etoz.ch/victoria-lounge-chair/",
	]










	