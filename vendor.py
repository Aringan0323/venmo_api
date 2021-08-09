from venmo_api import Client as VenmoClient
import json
import time


class Vendor:

    def __init__(self, seller_info_file, transaction_history_file, allow_tips=True):

        with open(seller_info_file) as f:

            self.seller_info = json.load(f)

        self.client = VenmoClient(access_token=self.seller_info['access_token'])

        self.transaction_history_file = transaction_history_file

        self.prev_id = ''

        self.allow_tips = allow_tips

    def new_transaction(self, trans):
        with open(self.transaction_history_file) as f:
            hist = json.load(f)
            f.close()
        unique_transaction = False
        if trans.payment_id not in hist['id_list']:
            hist['id_list'].append(trans.payment_id)
            unique_transaction = True
        with open(self.transaction_history_file, 'w') as outfile:
            json.dump(hist, outfile)
            outfile.close()
        return unique_transaction


    def dispense_item(self, item_num):

        print('Dispensing item {}'.format(item_num))
        time.sleep(3)


    def verify_transaction(self):

        recent_transactions = self.client.user.get_user_transactions(user_id=self.seller_info['user_id'], limit=5)
        for trans in recent_transactions:
            if self.new_transaction(trans):
                if (trans.note == self.seller_info['purchase_note']):
                    if (str(trans.payment_type) == 'pay'):
                        if trans.amount < self.seller_info['price_of_item']:
                            if trans.actor.username in self.seller_info['whitelist']:
                                self.client.payment.send_money(trans.amount, "It's your lucky day ;) {}".format(time.time()), trans.actor.id)
                                print('The customer is on the whitelist')
                            else:
                                self.client.payment.send_money(trans.amount, "Insufficient funds {}".format(time.time()), trans.actor.id)
                                print('The customer did not have the sufficient funds')
                        else:
                            change = trans.amount % self.seller_info['price_of_item']
                            num_items = int((trans.amount / self.seller_info['price_of_item']) - change)
                            if (change > 0) and self.allow_tips:
                                self.client.payment.send_money(change, "Here's your change for {} items {}".format(num_items, time.time()), trans.actor.id)
                                print("Sent the customer ${} in change".format(round(change,2)))
                            for i in range(num_items):
                                self.dispense_item(i)

                            # user_fee = (trans.amount-change)/10
                            # self.client.payment.send_money(user_fee, "user fee {}".format(time.time()), "2572350788730880067")

                            print('Payment completed')
                    else:
                        print('Incorrect transaction type')
                else:
                    print('Incorrect purchase note')
            else:
                print('Searching...')

        print('Search ended')
