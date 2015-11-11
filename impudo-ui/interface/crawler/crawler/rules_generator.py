import difflib
from difflib import SequenceMatcher
import re
from urlparse import urlparse

def remove_host(url):
	return urlparse(url).path

def longest_match(urls):
	result = urls[0]
	length = len(urls)
	for index in range(length-1):
		s = SequenceMatcher(None, result, urls[index+1])
		i, j, k = s.find_longest_match(0,len(result),0,len(urls[index+1]))
		result = result[i:i+k]

	return result

def generate_rule(urls):
	return re.escape(longest_match([remove_host(x) for x in urls]))


if __name__ == "__main__":

	urls = ["http://test.com/sdcs/add-to-cart=\"",
		"http://test.com/abxy/add-to-cart=\"",
		"http://test.com/bt67/add-to-cart=\"",
	]
	#example usage
	print generate_rule(urls)
