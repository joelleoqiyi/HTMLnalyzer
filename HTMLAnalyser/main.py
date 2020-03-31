from flask import Flask, render_template, request
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"]) 

def index():
  if request.method == "GET":
    return render_template('index.html')
  else:
    url = request.form.get("url")
    if url == "https://google.com":
      return render_template('easterEgg.html')
    return render_template('options.html', url=url)


@app.route('/options', methods=["GET", "POST"])

def options():
  if request.method == "GET":
	  return render_template('options.html')
  else: #post 
    url = request.form.get("url")
    tag_list = request.form.getlist("options_tag")
    raw_html = simple_get(url)
    htmll = BeautifulSoup(raw_html, 'html.parser') #type bs4
    prettifiedhtml = htmll.prettify() #type str
    print(htmll)
    tagged_dict = get_tag(tag_list, htmll)
    explanation = get_explanation(tagged_dict,htmll,url)
    return render_template('analyse.html', html=prettifiedhtml, explanation=explanation, url=url)

def simple_get(url):
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None
    except RequestException as e:
        log_error("Error during requests to {0} : {1}".format(url, str(e))) #prints the error msg lol
        return None

def is_good_response(resp):
    content_type = resp.headers['Content-Type'].lower() #converts all headers to lowercase
    return (resp.status_code == 200 and content_type is not None and content_type.find('html') >-1)
    #return the status_code and that content is not empty as well as finding the word html??

def log_error(e):
    print(e)

def get_tag(tag_list, html):
  tagged_dict = {}
  for tagging in tag_list:
    if html.select(tagging)  == []:
      print("No tag LOL")
      tagged_dict[tagging] = ["No such tag in HTML"]
      continue
    tagged_dict[tagging] = []
    for tagged in html.select(tagging):
      tagged_dict[tagging].append(tagged)
  return tagged_dict


def get_explanation(tagged_dict,htmll,url):
  explanation = []
  tagged_dict_tags = tagged_dict.keys()
  if len(tagged_dict_tags) == 0: #user chose nothing becoz if user chose something length will be more than 0
    explanation.append("You didn't choose any HTML tag to analyse? Click button below to choose again!")
  for explanationcounter, tags in enumerate(tagged_dict_tags):
    for number, curr_tag in enumerate(tagged_dict[tags]):
      if curr_tag == "No such tag in HTML":
        print("Moving On...")
        explanation.append("There is no '{0} tag' in the HTML from the link you provided...".format(tags))
        continue
      else:
        if number == 0:
          explanation.append("The following code {0} is a/an '{1} tag'. The code will do the following things: ".format(curr_tag, tags))#the default starting explanation if this is the first in the list
          #print(explanation[0] + '\n\n\n\n')
        else: 
          explanation[explanationcounter] = explanation[explanationcounter] + "\nThe following code {0} is a/an '{1} tag'. The code will do the following things: ".format(curr_tag, tags)#the default starting explanation if this is not the first in the list
          #print(explanation[0] + "\n\n\n\n")
        if curr_tag.text != '': #may need to check if it works or use "is not None"
          text = curr_tag.text 
          explanation[explanationcounter] = explanation[explanationcounter] + "\n -> Display the following text '{0}' ".format(text)
        if curr_tag.get('href') is not None: #if tags dont have its fine as it will just skip this 
          href = curr_tag.get('href')
          explanation[explanationcounter] += "\n -> When you click the text/tag, it will redirect you to the following link '{0}' ".format(href)
        if curr_tag.get('class') is not None: #universal 
          classs = curr_tag.get('class')#returns a list
          for classes in classs: 
            explanation[explanationcounter] += "\n -> Have a class of {0} attached to it. ".format(classes)
            inlinecss_str = select_style(htmll)
            inlinecss_searchkey = ".{0}".format(classes)
            explanation = get_style(inlinecss_searchkey, inlinecss_str, tags, explanation, explanationcounter)

        if curr_tag.get('id') is not None:
          idd = curr_tag.get('id')
          explanation[explanationcounter] += "\n -> Have a id of {0} attached to it. ".format(idd)
          inlinecss_str = select_style(htmll)
          inlinecss_searchkey = "#{0}".format(idd)
          explanation = get_style(inlinecss_searchkey, inlinecss_str, tags, explanation, explanationcounter)
        
        if curr_tag.get('src') is not None: #universal 
          srcc = curr_tag.get('src')
          srcc_str = str(srcc)
          if srcc_str[0:4] != 'http': #checks if the file is saved in the files
            if url[-1] == '/': #checks if behind has /
              url = url[0:-1] #remove the /
            if srcc_str[0] == '/':
              srcc_str = srcc_str[1:] #assume same folder
              pre_url(url, 1)
            elif srcc_str[0:2] == './': #same folder
              srcc_str = srcc_str[2:]
              pre_url(url, 1)
            elif srcc_str[0:3] == '../': #1 folder up
              srcc_str = srcc_str[3:]
              pre_url(url, 2)
            srcc_str = url + '/' + srcc_str #get the final src link
          explanation[explanationcounter] = explanation[explanationcounter] + "\n -> Display the picture at this location '{0}' ".format(srcc_str)

        if curr_tag.get('alt') is not None:
          altt = curr_tag.get('alt')
          altt_str = str(altt)
          explanation[explanationcounter] = explanation[explanationcounter] + "\n -> If the picture fails to be displayed, the following text will be displayed instead '{0}' ".format(altt_str)
        print (number)
      explanation[explanationcounter] += "\n"
  return explanation
  

def get_style(inlinecss_searchkey, inlinecss_str, tags, explanation, explanationcounter):
  inlinecss_search = inlinecss_str.find(inlinecss_searchkey)
  if inlinecss_search != -1:
    inlinecss_search_start = inlinecss_search+ len(inlinecss_searchkey)+1
    inlinecss_search_end = inlinecss_str[inlinecss_search_start:].find("}")+inlinecss_search_start #ends at }
    if inlinecss_searchkey[0] == '.': #class
      explanation[explanationcounter] += "And searching the style tag above, you can see that the following style(s) are attached to the class '{0}' which is then attached to this '{1} tag': ".format(inlinecss_searchkey[1:-1], tags)
      explanation[explanationcounter] += "\n -----> {0}".format(inlinecss_str[inlinecss_search_start: inlinecss_search_end])
    elif inlinecss_searchkey[0] == "#": #id
      explanation[explanationcounter] += "And searching the style tag above, you can see that the following style(s) are attached to the id '{0}' which is then attached to this '{1} tag': ".format(inlinecss_searchkey[1:-1], tags)
      explanation[explanationcounter] += "\n -----> {0}".format(inlinecss_str[inlinecss_search_start: inlinecss_search_end])
    else: #p, h1, h2, h3
      explanation[explanationcounter] += "And searching the style tag above, you can see that the following style(s) are directly attached to this '{1} tag': ".format(tags)
      explanation[explanationcounter] += "\n -----> {0}".format(inlinecss_str[inlinecss_search_start: inlinecss_search_end])
  elif inlinecss_searchkey[0] == ".":
    explanation[explanationcounter] += "And searching the style tag above, there is no style(s) attached to this class"
  elif inlinecss_searchkey[0] == "#":
    explanation[explanationcounter] += "And searching the style tag above, there is no style(s) attached to this id"
  else:
    explanation[explanationcounter] += "And searching the style tag above, there is no style(s) attached to this tag"
  return explanation

def select_style(htmll):
    inlinecss = htmll.select('style')
    inlinecss_str = str(inlinecss) #returns empty list if no inlinecss 
    return inlinecss_str

def pre_url(url, n):
  url = url.reverse()
  for i in range (2):
    slash = url.find('/')
    url = url[slash+1:]
  url = url.reverse()
  return url

@app.route('/redo', methods=["GET", "POST"]) #handles the returning of the webpage to previous page
def redo():
  url_query = request.form.get("url_query")
  return render_template('index.html', url=url_query)

app.run(host='0.0.0.0', port=8080)


'''
Some random notes: 

a tags 
  - href
  - text
  - style 
  - class
  - id 

h1,h2,h3,p tags
  - class
  - id
  - style
  - text

li tags
  - class
  - id
  - style
  - text

<IGNORE> ol, ul tags (ul.text prints out the text in the li tags.. cool!)
  - li tags 
  - class
  - id
  - style

img tag
  - src
  - alt?? (text)
  - class
  - id 
'''
