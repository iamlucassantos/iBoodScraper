"""
Created on 12/11/2020

@author: Lucas V. dos Santos
"""
from bs4 import BeautifulSoup
import requests


class WishList:

    def __init__(self, filename):
        self.items = []
        with open(filename, 'r') as f:
            for line in f:
                self.items.append(line.strip())

class Ibood:
    # find_all
    def __init__(self, url=None ):
        self.url = 'https://ibood.nl' if url is None else url

    def set_url(self, url):
        self.url = url

    def get_html(self):
        source = requests.get(self.url).text
        soup = BeautifulSoup(source, 'lxml')
        return soup


def main():
    a = Ibood()
    a.get_s()


if __name__ == "__main__":
    main()
