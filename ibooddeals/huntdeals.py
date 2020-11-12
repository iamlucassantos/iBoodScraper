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
        """Returns a dictionary with all information about a product"""
        html = self.get_html()
        product = None
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
        """If a match is found with the wishlist, a notification is created"""
        wish_list = WishList(wishlist_file).items
        notification = None
        product = self.get_product()
        for item in wish_list:
            if item.lower() in product['productName'].lower() or item.lower() in product['offerName'].lower():

                notification = Notify()
                timeend = re.search("(\d\d:\d\d:\d\d)", product['dealEndDateTime']).group(1)
                message = f"Price:  {product['price']} EUR \nDiscount: {product.get('discount','-')}% \nEnds: {timeend}"
                notification.title = product['productName']
                notification.message = message

        return product, notification

    def add_to_history(self, product):
        """ Adds all products to a history csv file"""

        with open('products_history.csv', 'a') as csvfile:
            fieldnames = ['productID', 'productName', 'offerName', 'price', 'dealStartDateTime', 'dealEndDateTime']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            with open('products_history.csv', 'r') as f:
                reader = csv.DictReader(f)

                if sum(1 for _ in f) == 0:  # Checks if file is empty
                    writer.writeheader()

                f.seek(0) # Returns to top of file


                APPEND = True
                for line in reader:  # Only appends if product not in the csv file yet
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
    prev_product = None
    while RUNNING is True:
        deal = HuntDeals()
        product, notification = deal.find_product_match('wishlist.txt')
        if product:
            if product != prev_product and notification:
                notification.send()
            prev_product = product
            deal.add_to_history(product)
        time.sleep(random.randint(15, 30))


if __name__ == "__main__":
    main()
