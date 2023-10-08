import pytest

from analyze import Contact

def test_simple():
	header = 'test <test@example.com>'

	c = Contact(header)
	assert c.email == 'test@example.com'
	assert c.name == 'test'

def test_spaces():
	header = 'A B C <test@example.com>'

	c = Contact(header)
	assert c.email == 'test@example.com'
	assert c.name == 'A B C'

def test_encoding_quotes():
	header = '"=?UTF-8?B?WnPDs2ZpYQ==?= =?UTF-8?B?IEtvdsOhY3M=?= (Meeting & Events - The Social Hub Amsterdam City)" <events.amscity@thesocialhub.co>'

	c = Contact(header)
	assert c.email == 'events.amscity@thesocialhub.co'
	assert c.name == 'Zsófia Kovács (Meeting & Events - The Social Hub Amsterdam City)'

def test_multiline():
	header = """=?utf-8?q?=D0=9E=D0=B1=D1=89=D0=B5=D1=81=D1=82=D0=B2=D0=BE_=D0=B0=D0=BD?=
	=?utf-8?q?=D0=BE=D0=BD=D0=B8=D0=BC=D0=BD=D1=8B=D1=85_=D1=82=D0=B5=D1=81?=
	=?utf-8?q?=D1=82=D0=B8=D1=80=D0=BE=D0=B2=D1=89=D0=B8=D0=BA=D0=BE=D0=B2?=
	<info@meetup.com>"""

	c = Contact(header)
	assert c.email == 'info@meetup.com'
	assert c.name == 'Общество анонимных тестировщиков'
