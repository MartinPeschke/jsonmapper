import simplejson, datetime
from itertools import izip_longest
from jsonmapper import Mapping, TextField, BaseUnitField, IntegerField, PictureField, DictField, DateTimeField, TypedField


class Merchant(Mapping):
  id = IntegerField()
  name = TextField()

class Product(Mapping):
  id = IntegerField()
  name = TextField()
  description = TextField()
  price = BaseUnitField()
  picture = PictureField()

class Venue(Mapping):
  id = IntegerField()
  name = TextField()
  description = TextField()
  line1 = TextField()
  line2 = TextField()
  post_code = TextField()
  city = TextField()
  area = TextField()
  picture = PictureField()
  merchant = DictField(Merchant, "Merchant")

class User(Mapping):
  id = IntegerField()
  name = TextField()
  picture = PictureField()
  facebook_id = TextField()
  email = TextField()
    
class Gift(Mapping):
  id = IntegerField()
  token = TextField()
  message = TextField()
  thankyou = TextField()
  status = TextField()
  created = DateTimeField()
  issued = DateTimeField()
  redeemed = DateTimeField()
  expiry = IntegerField()
  sender = DictField(User, "Sender")
  recipient = DictField(User, "Recipient")
  venue = DictField(Venue, "Venue")
  product = DictField(Product, "Product")

  def isOpen(self):
      return self.status == 'OPEN'
  def isIssued(self):
      return self.status == 'ISSUED'
  def isRedeemed(self):
      return self.status == 'REDEEMED'
  def isExpired(self):
    return self.expiry < 0

  def expiresIn(self):
    expiry = self.expiry
    if expiry:
      if expiry == 1:
        return '1 day'
      if expiry < 7:
        return '{} days'.format(expiry)
      if expiry < 31:
        return "{} weeks".format(expiry/7)
      if expiry < 365:
        return "{} months".format(expiry/30)
      return "{} years".format(expiry/365)

  def getProductRepr(self):
    return self.product.name
  def getPrettyPrice(self):
      return "&pound; {}".format(self.product.price)
  def isForMe(self, u_id):
    return self.recipient.id == u_id 
    
g = Gift.wrap({"id":"813","token":"0AF685DF-9505-4EC5-A411-7BFAB3105C7E","Recipient":{"id":"254","name":"Mapa Technorac","facebook_id":"100000924808399","picture":"http://graph.facebook.com/100000924808399/picture"},"Sender":{"id":"539","name":"Grant Hutchinson","facebook_id":"100001848870955","email":"test77@friendfund.com","picture":"http://graph.facebook.com/100001848870955/picture"},"Product":{"name":"Chablis","price":"330","description":"A relaxing Glass of Wine","id":"2","picture":"/pics/products/pint_.png"},"Venue":{"id":"5","name":"The Jolly Butchers","line1":"5 the street","line2":"a street","post_code":"l1","city":"London","area":"Notting Hill","picture":"/pics/venues/temp.jpg","description":"the best venue in town","Merchant":{"id":"3","name":"Bass"}},"message":"Hello Mate, this is awesome and works nice! Well done! Get thepint on me! You've earned it!","status":"REDEEMED","issued":"2012-02-21T08:49:42.050","redeemed":"2012-02-21T08:50:08.287","created":"2012-02-17T19:12:37.107","expiry":"-5"})

from decimal import Decimal

assert g.product.price == Decimal("3.30")
assert g.isExpired() == True
assert g.sender.name == "Grant Hutchinson"
assert g.recipient.name == "Mapa Technorac"
assert g.thankyou == None
assert str(g.created) == '2012-02-17 19:12:37'
assert g.created.year == 2012




def grouper(n, iterable, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return izip_longest(*args, fillvalue=fillvalue)

class CardDetails(Mapping):
  type = TextField()
  number = TextField(name='card_number')
  def getSavedGroupedDetails(self, no):
    self._cc_groupings = list(map("".join, grouper(4, self.number, " ")))
    return self._cc_groupings[no]

class AmexCardDetails(CardDetails):
  cvc_length = 4
  cvc_max = 9999
  cvc_hint = "4 digit code on the front of your credit card"

class CreditCardDetails(CardDetails):
  cvc_length = 3
  cvc_max = 999
  cvc_hint = "3 digit code on the back of your credit card"

class User(Mapping):
  id = IntegerField()
  name = TextField()
  picture = PictureField()
  access_token = TextField()
  user_token = TextField()
  facebook_id = TextField()
  email = TextField()
  saved_card_details = TypedField({'AMEX': AmexCardDetails, 'VISA': CreditCardDetails, 'MC': CreditCardDetails}, type_key='type', name="SavedDetails")

  def isAnon(self):
    return self.id is None

  def isMe(self, user_map):
    return (not self.isAnon()) and (self.facebook_id == user_map.get('facebook_id') or self.email == user_map.get('email'))

  def isAnonJSON(self):
      return simplejson.dumps(self.isAnon())
  def toJSON(self):
    return simplejson.dumps(self.unwrap())
  def hasSavedDetails(self):
    return self.saved_card_details is not None

assert User().isAnon() == True
u = User.wrap({"id":"254","access_token":"AAADipxqvveoBAAfcvgGqVshOj03XcarNAijDZCqz45KZCHNL7MKK5nw41n4luNQjNneTtmqkBGUVOFSRaM1ht6RZCV0LjSDkTpaD9VlFgZDZD","user_token":"B6FBC0F1-04E5-40A4-AE1D-4D4B40369BAB","name":"Mapa Technorac","facebook_id":"100000924808399","email":"martin.peschke@gmx.net","picture":"http://graph.facebook.com/100000924808399/picture","SavedDetails":{"card_number":"xxxxxxxxxxxx002","type":"AMEX"}})
assert u.saved_card_details.getSavedGroupedDetails(0) == 'xxxx'
assert u.saved_card_details.getSavedGroupedDetails(1) == 'xxxx'
assert u.saved_card_details.getSavedGroupedDetails(2) == 'xxxx'
assert u.saved_card_details.getSavedGroupedDetails(3) == '002 '


from backend import RemoteProc
def backend(root_key, url, method, data):
  return {"status":0,"proc_name":"get_catalog","Category":[{"name":"Pubs & Bars","id":"1","picture":"/pics/categories/pint_.png","Product":[{"name":"4486e546-5ae5-4975-881d-9eac69e3926e","description":"A lovely refreshing pint","id":"1","picture":"sd"},{"name":"Half Pint","description":"Something to refresh the senses","id":"4","picture":"/pics/products/shot_.png"},{"name":"Wine","description":"Something to cheer you up","id":"5","picture":"/pics/products/wine_.png"},{"name":"harry","description":"sadfsdafsdf","id":"73","picture":"594bd79a-fa04-46e7-b4cb-9e6a83b5610f.png"},{"name":"A box full of Chocolate","description":"Get a hot box now, while its cool","id":"76","picture":"0378cbad-71b1-425a-aaed-74465611dbe2.jpg"},{"name":"37ca1b82-0de4-42d4-862a-8566cda726b2","description":"something delicious","id":"111","picture":"sd"},{"name":"deba23e7-b373-4dcd-b572-e8f5158f8d52","description":"something delicious","id":"112","picture":"sd"},{"name":"9c97ce25-fc92-4376-b644-6635d1e3d79f","description":"something delicious","id":"113","picture":"sd"},{"name":"26e68601-5c8b-4034-866f-1306e208340e","description":"something delicious","id":"114","picture":"sd"},{"name":"ee66c31c-ae23-4186-9025-16e51abd58d1","description":"something delicious","id":"115","picture":"sd"},{"name":"23018f52-83f6-4e1d-8458-c5cbba186603","description":"something delicious","id":"116","picture":"sd"},{"name":"fb153fb2-8f96-47de-a57a-6ed2662aa873","description":"something delicious","id":"117","picture":"sd"},{"name":"e0c0be2f-1b60-432f-8748-74d808dbbfd5","description":"something delicious","id":"118","picture":"sd"},{"name":"f9dfde01-0771-417a-9553-3785cfd1d1e8","description":"something delicious","id":"119","picture":"sd"},{"name":"b274e179-3832-41dc-91eb-6006a59618c2","description":"something delicious","id":"120","picture":"sd"},{"name":"e840346a-8abc-436c-a9aa-f4b8e8e9149c","description":"something delicious","id":"121","picture":"sd"},{"name":"9d7decdb-fbce-44d7-a519-9fb080851210","description":"something delicious","id":"122","picture":"sd"},{"name":"7c195df4-18e0-40ae-a7a8-ade42a468ec8","description":"something delicious","id":"123","picture":"sd"},{"name":"4afdc267-8e47-4540-baf2-4fc14dc205cc","description":"something delicious","id":"124","picture":"sd"},{"name":"3d268e0c-0b15-4f25-9d84-a58f546db1ab","description":"something delicious","id":"125","picture":"sd"},{"name":"1c393398-f38d-427f-a49e-2d592d29e1e6","description":"something delicious","id":"126","picture":"sd"}]},{"name":"Cafes","id":"2","picture":"/pics/categories/wine_.png","Product":[{"name":"Dinner for two","description":"A great night out","id":"6","picture":"/pics/products/pint_.png"},{"name":"Danish","description":"Sweet tooth","id":"21","picture":"/static/img/products/wine_.png"}]},{"name":"Wine Merchant","id":"3","picture":"009c1d77-996c-4bc3-9174-8efa3dcd5071.jpg","Product":[{"name":"Red or White","description":"Delicious and nutrious","id":"3","picture":"/pics/products/pint_.png"}]},{"name":"Ice Cream","id":"4","picture":"262212df-48f0-4188-960f-feb276ead266.jpg","Product":[{"name":"Chablis","description":"A relaxing Glass of Wine","id":"2","picture":"/pics/products/pint_.png"}]},{"name":"be094f2b-c843-454b-93a1-7e59d3b6d5f9","id":"33","picture":"as"},{"name":"8a359a16-d4f9-45af-b106-dc24d90d56d2","id":"34","picture":"as"},{"name":"6fb67bca-d1b7-4963-bb8c-5851056fbd66","id":"35","picture":"as"},{"name":"c4095b84-3a5b-46c8-bd88-267e8315846d","id":"36","picture":"as"},{"name":"7ad81ecb-e155-4569-aa92-5c68e6f6f27e","id":"37","picture":"as"},{"name":"a3c59390-0eda-4805-83e9-485cae9eb2c4","id":"38","picture":"as"},{"name":"1560fd37-d12e-4e6e-bee8-3211908137ce","id":"39","picture":"as"},{"name":"4a3fc098-3e35-4cf6-af4d-cd3af08b7cde","id":"40","picture":"as"},{"name":"61f2e693-a0fc-44c6-992f-571195f03b3c","id":"41","picture":"as"},{"name":"2ee6e07b-bb54-442e-b7a9-92ad6a32bc80","id":"42","picture":"as"},{"name":"557040df-befa-4396-bb32-f19a241cf165","id":"43","picture":"as"},{"name":"ca19a42b-0b0f-4179-95cf-cc050ac6a52f","id":"44","picture":"as"},{"name":"853469e1-16e1-43ee-8bc6-9ca15cee4cf3","id":"45","picture":"as"},{"name":"64f1ce68-c9c2-416a-833a-7767ba1147cb","id":"46","picture":"as"},{"name":"52637ded-cca1-4e2e-8ce1-2d760a0a3c55","id":"47","picture":"as"},{"name":"c8e4c61e-05b7-4dbc-807d-bc0a418cf1fe","id":"48","picture":"as"}]}


rp = RemoteProc("/api/product/catalog", "POST", 'User', User)
print rp(backend, {"id":"1"})




