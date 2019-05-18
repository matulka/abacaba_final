class OrderProductInformation:  # #A class for storing information for an order product
    def __init__(self, quantity, stock_product):
        self.quantity = quantity
        self.stock_product = stock_product
        self.id = None
