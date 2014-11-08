
from datetime import datetime
import random
from base64 import b64encode

from Crypto.Cipher import AES

from . import db, BaseMixin

TSHIRT_SIZES = [
    ('0',  u''),
    ('1', u'XS'),
    ('2', u'S'),
    ('3', u'M'),
    ('4', u'L'),
    ('5', u'XL'),
    ('6', u'XXL'),
    ('7', u'XXXL'),
    ]

PRINTABLE_ASCII = map(chr, range(32, 127))

def rand_printable_string(length):
    chars = ['x'] * length
    for i in range(0, length):
        chars[i] = random.choice(PRINTABLE_ASCII)
    return "".join(chars)

def pad16x(string):
    extra = len(string) % 16
    if extra > 0:
        return string + 'x' * (16 - extra)
    else: return string

def pad_secret(secret, n=16):
    assert(len(secret) <= n)
    padn = n - len(secret)
    return secret + 'x' * padn

def encrypt_field(aes, x):
    n = len(x)
    return dict(n=n, d=b64encode(aes.encrypt(pad16x(x))))

def encrypt_participant(row):

    # TODO: make this configurable
    IV456 = "must be 16 bytes"

    # Fields to export
    FIELDS = [ "name"
             , "email"
             , "phone"
             , "company"
             , "city"
             , "twitter"
             ]

    # Encrypt each row
    aes = AES.new(pad_secret(row.secret, 16), AES.MODE_CBC, IV456)
    return dict(zip(FIELDS,
                    [encrypt_field(aes, str(getattr(row, f))) \
                        for f in FIELDS])
                , id=row.id
                , public=row.public
           )

class Participant(db.Model, BaseMixin):
  
    __tablename__ = 'participant'
    
    #: Ticket number
    ticket_number = db.Column(db.Unicode(15), nullable=True)
    #: Name of the participant
    name = db.Column(db.Unicode(80), nullable=False)
    #: Email of the participant
    email = db.Column(db.Unicode(80), nullable=False)
    #: Company name
    company = db.Column(db.Unicode(80), nullable=True)
    #: Job title
    job = db.Column(db.Unicode(80), nullable=True)
    #: City
    city = db.Column(db.Unicode(80), nullable=True)
    #: Phone
    phone = db.Column(db.Unicode(25), nullable=True)
    #: Twitter handle
    twitter = db.Column(db.Unicode(80), nullable=True)
    #: base64 encoded gravatar image
    image = db.Column(db.Text, default='LOAD', nullable=True)
    #: Whether the participant is a Speaker at the event
    speaker = db.Column(db.Boolean, default=False, nullable=False)
    #: Whether the participant has purchased a T-shirt
    purchased_tee = db.Column(db.Boolean, default=False, nullable=True)
    #: Date of registration
    regdate = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    #: NFC ID
    nfc_id = db.Column(db.Unicode(80), nullable=True, default=None)
    #: Public key - key for looking up records at Kiosk
    public = db.Column(db.Unicode(4), nullable=False, default=None)
    #: Secret - secret key for AES encryption
    secret = db.Column(db.Unicode(20), nullable=False, default=None)
    #: Source of registration, whether online(True) or offline(False)
    online_reg = db.Column(db.Boolean, default=True, nullable=True)
    #: Order ID
    order_id = db.Column(db.Integer, nullable=True)
    #: Purchases made by the participant
    purchases = db.Column(db.Unicode(200), nullable=True)
    #: Additional notes for a participant
    notes = db.Column(db.Unicode, nullable=True)
    #: Event the participant is attending
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))

    __table_args__ = (db.UniqueConstraint('event_id', 'nfc_id'), db.UniqueConstraint('event_id', 'email', 'name'), db.UniqueConstraint('event_id', 'ticket_number'))

    def __repr__(self):
        return self.name
