#!/usr/bin/python
# -*- coding: UTF-8 -*-
import stripe

print "Content-Type: text/plain;charset=utf-8"
print

try:
	stripe.api_key = "sk_live_Vz9P2rMdfp108PwJHhLg8Xp6"
	customer_id = "cus_4pGuziZOYNzxga"
        customer = stripe.Customer.retrieve(customer_id)
        print str(customer)

  
except stripe.error.StripeError, e:
	print "error"
	pass

print "testing chargin stripe library"
	