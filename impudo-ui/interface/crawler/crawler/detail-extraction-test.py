# -*- coding: utf-8 -*-
import re

from dao import Dao

testmoneystring = """i have 1434445444554445737$ and $45 and 6 USD and 5€ 56 Dollar
154543534544$ i$5dollar

4£

7.56 dOlLar


 Nationalmuseum/ LM-77677 CHF 750
21,000.- €

$21,000.- 


$ 21,000.- 

0
45USD
13.40 USD
1
33
555
£4,656
4656
99,785£
125,944
7,994,169
7994169
0.00
1.00
33.78795
555.12
4,656.489
99,785.01
125,944.100
123 123.00 $123.00 1234 $1234 $1234.00 $1,234.00

21,000.- DKK

5.7
.7
0.70
1,000
1.000
4.50
4,50

1,000,000
1000000

123 123.00 

$123.00 
1234 
$1234 

$1234.00 

$1,234.00

3 EUR
EUR 3
€ 3
3€

£4
4 £
4£
3 GBP
GBP 3
50p
50 pence

$4
$ 4
4 $
4 USD
USD 5
4 US$
US$ 4

50c
50¢
50 cent

4 AUD
AUD 5
$A
AU$


4 CAD
CAD 3

4 HKD
HKD 3

4 MXN
MXN 4

3 CHF
3 Fr.
12 Rp.

CHF 3
Fr. 3
Rp. 12

5 TRY
TRY 5
5 ₺
₺ 5

NOK 5
5 NOK
DKK 5
5 DKK
5 kr.
kr. 5

5 kr
kr 5

3 ¥
¥ 3
3 JPY
JPY 3

3 ₽
₽ 3
3 RUB
RUB 3

3 CNY
CNY 3



"""
testdimensionstring = """Cm 45x109; cm 56 x 80 x 52,5h
168x53 H87; 120x51 H 93
L: 107 W: 4 H: 34 cm
B:140, T: 70, H: 72
height: 52 cm
width: 57 cm
depth: 37 cm
Dimensions: 64W x 35D x 56H cm
 Height: 271cm (106.7’’) 
•  Width: 178cm (70.1’’) 
•  Depth: 65cm (25.6’’)
150 x 45 / H. 100
200cm wide x 75cm deep x 80cm high
Dia35cm H26cm L93cm
•	Dimensions: W 43cm (16.9")H 80cm (31.5")D 12cm (4.7") 
Höhe: 93cm
Breite: 110cm
Tiefe: 65cm
Dimensions : 49cm x 43cm et hauteur 75cm
Dimensions: W 75 x D 77 x H 80 / seat: 38 cm
HxBrxD 150x58x36
Afmetingen: breed 135 cm, diep cm, hoogte 77 cm, zithoogte ca. 40 cm.
Hoogte: 35 cm
Diameter: 27 cm
Dimensions
Width	100 cm
Height	75 cm
Depth	75 cm
L 200cm D82cm H48cmSOLD
Sizes: W 63 x D 60 x H 80 cm 
Seat Height: 44 cm
Chair dimensions are: 
Total height: 107 cm 
Width: 86 cm 
Depth: 79 (95) cm
Footstool dimensions are: 
Height: 37 cm 
Width: 56 cm 
Depth: 41 cm
Höhe	70 cm
Durchmesser Sitzplatte	34 cm
Measurements: H: 34 cm, diameter: 15 cm.
Größe	9 x 9 x 9 cm
Größe in centimeter 
H: 73; B: 55,5; L: 68
Dimensions: 40x50cm
Measure H: 45cm. W: 31x31cm.
hauteur 50cm, largeur 59cm, profondeur 39cm
L110/P60H72 cm
Dim : 67 x 52 x (h) 145 cm
We have four smaller lamps (22cm) and one bigger one (30cm)
H: 60cm 
W: 120cm 
D: 55cm
5 cm x 5 cm x 5cm
5 cm x 5 cm
5 cm

3 m
2mm
3"
2'

1'5"

1'5


3 in
3 ft

"""

def extract_price_and_dimensions(text):

	#moneyregexold = r"""[+-]?[0-9]{1,3}(?:[0-9]*(?:[.,][0-9]{2})?(?:\.-)?|(?:,[0-9]{3})*(?:\.[0-9]{2})?(?:\.-)?|(?:\.[0-9]{3})*(?:,[0-9]{2})?)?(?:\.-)?"""
	moneyregex = r"""[0-9]+(?:[,.]?[0-9]+)*(?:\.-)?"""
	
	#fullwordonly1= r"""(?:^|\s)"""
	#fullwordonly2= r"""(?:$|\s)"""
	#example usage:
	#moneymatch = "(?:"+fullwordonly1+currenciespattern+moneyregex+fullwordonly2+")|(?:"+fullwordonly1+moneyregex+currenciespattern+fullwordonly2+")"
	
	currenciespattern = r"""(?:€|\$|£|EUR|USD|Euro|Dollar|DKK|GBP|AUD|AU\$|CAD|HKD|MXN|CHF|DKK|NOK|Fr\.|¥|JPY|₽|RUB|CNY)"""
	#moneymatch = "(?:"+currenciespattern+ r"[ \t]?"+moneyregex+ r")|(?:" +moneyregex+ r"[ \t]?" +currenciespattern+ ")"
	moneymatch = "(?:" +currenciespattern+ r"[ \t]?"+moneyregex+ r")|(?:(?:\s)" +moneyregex+ r"[ \t]?" +currenciespattern+ ")"

	#to match dimensions in text
	lnum = r"""(?:[0-9]*\,[0-9]+|[0-9]*\.[0-9]+|[0-9]+)"""
	lwh = r"""(?:d|D|w|W|h|H|T|t|L|B)"""
	lunit = r"""(?:mm|cm|dm|"|’’|'|’|'')"""

	#dimmatch = "("+lnum + r"[ \t]?x[ \t]?"+lnum  + r"(?:[ \t]?x[ \t]?" +lnum+ r")?" +"|"+lnum+ r"[ \t]*"+lwh+r"*[ \t]*"+lunit+"|"+lnum+lwh+"|"+r"\b"+lwh+ r"(\:|\.)?[ \t]*"+lnum+ r"[ \t]?"+lunit+"?" +")" 
	dimmatch = "("+lnum +r"[ \t]?" +lunit+"?" + r"[ \t]?x[ \t]?"+lnum +r"[ \t]?" +lunit+"?" + r"(?:[ \t]?x[ \t]?" +lnum +r"[ \t]?" +lunit+"?" + r")?" +"|"+lnum+ r"[ \t]*"+lwh+r"*[ \t]*"+lunit+"|"+lnum+lwh+"|"+r"\b"+lwh+ r"(\:|\.)?[ \t]*"+lnum+ r"[ \t]?"+lunit+"?" +")" 

	moneymatches = []

	for r in re.findall(moneymatch,text,re.IGNORECASE):
		if r:
			moneymatches.append(r)

	dimensionmatches = []

	for r in re.findall(dimmatch,text,re.IGNORECASE):
		if r[0]:
			dimensionmatches.append(r[0])


	return (moneymatches,dimensionmatches)


def extract_and_save_details(id, title, content):
	#extract from content
	x = extract_price_and_dimensions(content)

	foundprices = ""
	for a in x[0]:
		foundprices += "".join(a.split()) + " " 
	foundprices = foundprices.strip()

	founddims = ""
	for a in x[1]:
		founddims += "".join(a.split()) + " " 
	founddims = founddims.strip()

	#extract from title
	x = extract_price_and_dimensions(title)
	for a in x[0]:
		foundprices += "".join(a.split()) + " " 
	foundprices = foundprices.strip()
	for a in x[1]:
		founddims += "".join(a.split()) + " " 
	founddims = founddims.strip()

	d.insert_record_details(id,foundprices,founddims)
















