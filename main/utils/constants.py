
#Variables
SINGLE = "single"
MULTIPLE = "multiple"

DIAMOND = "diamond"
CLUB = "club"

STUDENT = 'student'
VENDOR = 'vendor'




#Tuples
MODE = (
    (SINGLE, "Single"),
    (MULTIPLE, "Multiple"),
)


CARD_TYPES = (
    (DIAMOND, "Diamond"),
    (CLUB, "Club"),
)

USER_CATEGORY = (
    (STUDENT, "Student"),
    (VENDOR, "Vendor"),
)

TRANSACTION_TYPES = [
        ('debit', 'Debit'),
        ('credit', 'Credit'),
    ]

class SendPointsConstant():

    DIRECT = 'direct'
    TICKET = 'ticket'