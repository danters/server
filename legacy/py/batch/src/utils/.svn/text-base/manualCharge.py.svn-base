#!/usr/bin/python
# -*- coding: UTF-8 -*-
import stripe

print "Content-Type: text/plain;charset=utf-8"
print

try:
	stripe.api_key = "sk_live_Vz9P2rMdfp108PwJHhLg8Xp6"
	customer_id = "cus_4pGuziZOYNzxga"
	stripe.Charge.create(
	    amount=600, # 200 is $2.00
	    currency="usd",
	    customer=customer_id,
            description="ValetAnywhere Services"
	)

  
except stripe.error.StripeError, e:
	print "error"
	pass

print "testing chargin stripe library"
	