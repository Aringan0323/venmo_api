import keyboard
from vendor import Vendor



if __name__ == '__main__':

    vendor = Vendor('seller_info.json', 'transaction_history.json')

    while True:
        keyboard.wait('p')
        print('Key pressed')
        vendor.verify_transaction()
