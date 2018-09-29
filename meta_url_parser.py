#!/usr/bin/env python
# -*- coding: utf-8 -*-

#importing the libraries
from urllib import urlopen
from bs4 import BeautifulSoup
from urllib import FancyURLopener

class MyOpener(FancyURLopener):
    version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'

mopen = MyOpener()

def get_title(data):
        title = "Sem titulo disponível"
        tag = data.find("meta",  property="og:title")
        if tag:
            title = tag["content"]
            return title
        tag = data.find("meta", {"name":"twitter:title"})
        if tag:
            title = tag["content"]
            return title
        tag = data.find("meta", {"name":"title"})
        if tag:
            title = tag["content"]
            return title
        
        tag = data.find('title')
        if tag:
            title = tag.renderContents()
            return title
           
        tag = data.find('h1')
        if tag:
            title = tag.renderContents()
            return title
        
        return title
 

def get_description(data):
        description = "Sem descrição disponível"
        tag = data.find("meta",  property="og:description")
        if tag:
            description = tag["content"]
            return description
        tag = data.find("meta", {"name":"twitter:description"})
        if tag:
            description = tag["content"]
            return description
        tag = data.find("meta", {"name":"description"})
        if tag:
            description = tag["content"]
            return description
        return description
 


def get_image(data):
        image = "Sem_imagem.jpeg"
        tag = data.find("meta",  property="og:image")
        if tag:
            image = tag["content"]
            return image
        tag = data.find("meta", {"name":"twitter:image"})
        if tag:
            image = tag["content"]
            return image
        tag = data.find("meta", {"name":"image"})
        if tag:
            image = tag["content"]
            return image
        return image




def get_author(data, url):
        author = url
        tag = data.find("meta",  property="og:author")
        if tag:
            author = tag["content"]
            return author
        tag = data.find("meta", {"name":"twitter:author"})
        if tag:
            author = tag["content"]
            return author
        tag = data.find("meta", {"name":"author"})
        if tag:
            author = tag["content"]
            return author
        tag = data.find("meta",  property="og:site_name")
        if tag:
            author = tag["content"]
            return author
        return author


def get_date(data):
        tag = data.find("meta",  property="article:published_time")
        return(tag["content"] if tag else "sem data")



def get_keywords(data):
    keywords = "keywords"
    tag = data.find("meta", {"name":"keywords"})
    if tag:
        keywords = keywords + ', ' + tag["content"]
        
    tag = data.findAll("meta",  property="article:tag")
    if tag:
        for item in tag:
            #print item["content"]
            #item = item.split("content=")[0]
            keywords = keywords + ", " + item["content"]
    
    return keywords



def get_metadata(url):
    url = process_url(url)
    data = get_url_data(url)
    print(get_title(data))
    print(get_author(data, url))
    print(get_description(data))
    print(get_image(data))
    print(get_date(data))
    print(get_keywords(data))
    print("\n\n\n")


def get_url_data(url):
    webpage = str(mopen.open(url).read())#str(urlopen(url).read())
    soup = BeautifulSoup(webpage, "html.parser")
    return soup


def process_url(url):
    http = "http"
    if url.find(http) <0:
        url = "https://"+ url
    return url


if __name__ == '__main__':
    u1 = "https://clebertoledo.com.br/politica/em-reuniao-com-presenca-de-adir-vicentinho-confirma-conversa-com-amastha-e-marca-convencao-para-mesmo-dia-do-psb/"
    u2 = "https://paranaportal.uol.com.br/politica/pericia-aponta-que-odebrecht-nao-aplicou-r-700-mil-em-obras-do-sitio-de-atibaia/"
    u3 = "www.justica.gov.br/seus-direitos/classificacao"
    u4 = "https://www.youtube.com/watch?v=srzSYQjM_j4&feature=youtu.be"
    u5 = "http://www.agmarrios.com.br/2018/07/4-cavalgada-2-amigos-e-realizada-com.html"

    get_metadata(u1)
    get_metadata(u2)
    get_metadata(u3)
    get_metadata(u4)
    get_metadata(u5)
