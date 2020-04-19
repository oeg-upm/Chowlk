import bs4
from bs4 import BeautifulSoup
import html


data = html.unescape('&lt;div&gt;&lt;b&gt;kpi:&lt;/b&gt; http://theontology.namespace.com&lt;/'
                     'div&gt;&lt;div&gt;&lt;b&gt;s4bldg:&lt;/b&gt; http://reusedontologies.com&lt;br&gt;&lt;/div&gt;')
soup = BeautifulSoup(data, features="html.parser")

for div in soup:
    print(str(div.contents[1]))