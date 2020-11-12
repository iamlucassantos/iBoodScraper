"""
Created on 12/11/2020

@author: Lucas V. dos Santos
"""

from ibooddeals.helpers import WishList, Ibood
import re
from notifypy import Notify
import time
import random
import csv

class HuntDeals(Ibood):

    def __init__(self, url=None):
        super().__init__(url)

    def get_product(self):
        html = self.get_html()
        for script in html.find_all('script'):
            pattern = re.compile("product.push\(\s+(\{[\s\S]*),\s+\);\s+return product;")
            json_data = script.find(text=pattern)
            if json_data:
                product = dict()
                data = pattern.search(json_data).group(1)
                for line in data.splitlines():
                    if ':' in line:
                        results = re.search("(\w+):\ '(.*?)'", line)
                        if results:
                            product[results.group(1)] = results.group(2)

        return product

    def find_product_match(self, wishlist_file=None):

        wish_list = WishList(wishlist_file).items

        product = self.get_product()
        for item in wish_list:
            if item.lower() in product['productName'].lower() or item.lower() in product['offerName'].lower():

                notification = Notify()
                time = re.search("(\d\d:\d\d:\d\d)", product['dealEndDateTime']).group(1)
                message = f"Price:  {product['price']} EUR \nDiscount: {product.get('discount','-')}% \nEnds: {time}"
                notification.title = product['productName']
                notification.message = message
                notification.send()

        return product

    def add_to_history(self, product):

        with open('products_history.csv', 'a') as csvfile:
            fieldnames = ['productID', 'productName', 'offerName', 'price', 'dealStartDateTime', 'dealEndDateTime']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            with open('products_history.csv', 'r') as f:

                if sum(1 for _ in f) == 0:
                    writer.writeheader()
                f.seek(0)
                reader = csv.DictReader(f)
                APPEND = True
                for line in reader:
                    if line['productID'] == product['productID']:
                        APPEND = False
                        break

                if APPEND:
                    row_to_write = dict()
                    for field in fieldnames:
                        row_to_write[field] = product[field]
                    writer.writerow(row_to_write)

def main():
    RUNNING = True
    while RUNNING is True:
        deal = HuntDeals()
        product = deal.find_product_match('wishlist.txt')
        deal.add_to_history(product)
        time.sleep(random.randint(15, 30))


if __name__ == "__main__":
    main()
