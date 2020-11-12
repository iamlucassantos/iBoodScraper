class WishList:

    def __init__(self, filename):
        self.items = []
        with open(filename, 'r') as f:
            for line in f:
                self.items.append(line.strip())


