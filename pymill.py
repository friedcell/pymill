#! /usr/bin/env python
# -*- coding: utf-8 -*-
#pymill.py

import pycurl, cStringIO, json


class Pymill():
    """
    CC object desc:
    id: unique card ID
    card_type: visa, mastercard, american express
    country: country the card was issued in
    expire_month: (2ch)
    expire_year: (4ch)
    card_holder: name of cardholder
    last4: last 4 digits of card
    created_at: unixtime
    updated_at: unixtime
    """
    
    def __init__(self, privatekey):
        """
        Initialize a new paymill interface connection. Requires a private key.
        """
        self.c=pycurl.Curl()
        self.c.setopt(pycurl.NOSIGNAL, 1)
        self.c.setopt(pycurl.CONNECTTIMEOUT, 30)
        self.c.setopt(pycurl.USERPWD, '%s:' % (privatekey,))
        
    def _post(self,url,params=()):
        """
        Posts a request with parameters to a given url
        url: The URL of the entity to post to.
        params: a tuple of (name, value) tuples of parameters
        
        Returns None
        """
        self.c.setopt(self.c.URL, url)
        if params is not ():
            p=str("&".join([i[0]+"="+i[1] for i in params]))
            print p
            self.c.setopt(pycurl.CUSTOMREQUEST, "POST")
            self.c.setopt(self.c.POSTFIELDS,p)
        self.c.perform()
        
    def _apicall(self,url,params=(),cr="GET"):
        """
        Call an API endpoint.
        url: The URL of the entity to post to.
        params: a tuple of (name, value) tuples of parameters
        cr: The request type to be made. If parameters are passed, this will be ignored and treated as POST
        
        Returns a dictionary object populated with the json returned.
        """
        self.c.setopt(pycurl.CUSTOMREQUEST, cr)
        buf=cStringIO.StringIO()
        self.c.setopt(self.c.WRITEFUNCTION, buf.write)
        self._post(url, params)
        s=buf.getvalue()
        buf.close()
        return json.loads(s)

    def newcard(self,token):
        """
        Create a credit card from a given token.
        token: string Unique credit card token
        
        Returns: a dict representing a CC
        """
        return self._apicall("https://api.paymill.de/v1/creditcards",(("token", token),))

    def getcarddetails(self, cardid):
        """
        Get the details of a credit card from its id.
        cardid: string Unique id for the credit card
        
        Returns: a dict representing a CC
        """
        return self._apicall("https://api.paymill.de/v1/creditcards/"+str(cardid))
    
    
    def getcards(self):
        """
        List all stored cards.
        
        Returns: a dict with a member "data" which is an array of dicts, each representing a CC
        """
        return self._apicall("https://api.paymill.de/v1/creditcards/")

        
    def delcard(self, cardid):
        """
        Delete a stored CC
        cardid: Unique id for the CC to be deleted
        
        Returns: a disct with an member "data" containing an empty array
        """
        return self._apicall("https://api.paymill.de/v1/creditcards/%s"%(str(cardid),),cr="DELETE")
        
        
    def transact(self, amount=0, currency="eur", description=None, token=None, client=None, card=None):
        """
        Create a transaction (charge a card). You must provide an amount, and exactly one funding source.
        The amount is in Eurocents, and the funding source can be a client, a token, or a card id.
        amount: The amount (in Euro CENTS) to be charged. For example, 240 will charge 2 euros and 40 cents, NOT 240 euros.
        currency: Must be "eur" if given (optional)
        description: A short description of the transaction (optional)
        token: A token generated by the paymill bridge js library
        client: A client id number
        creditcard: A CC id number.
        
        Returns: None if one of the required parameters is missing. A dict with a member "data" containing a transaction dict otherwise.
        """
        
        p=[]
        if token is not None:
            p+=[("token",token)]
        elif client is not None:
            p+=[("client",client)]
        elif card is not None:
            p+=[("creditcard",card)]
        else:
            return None
        if amount==0:
            return None
        if description is not None:
            p+=[("description",description)]
        p+=[("amount",str(amount))]
        p+=[("currency",currency)]
        return self._apicall("https://api.paymill.de/v1/transactions/",tuple(p))
                
    def gettrandetails(self, tranid):
        """
        Get details on a transaction.
        tranid: string Unique id for the transaction
        
        Returns: a dict representing a transaction
        """
        return self._apicall("https://api.paymill.de/v1/transactions/"+str(cardid))
    
    
    def gettrans(self):
        """
        List all transactions.
        
        Returns: an array of dicts with a member "data" which is an array of dicts, each representing a transaction
        """
        return self._apicall("https://api.paymill.de/v1/transactions/")

    def refund(self,tranid, amount, description=None):
        """
        Refunds an already performed transaction.
        tranid: string Unique transaction id
        amount: The amount in cents that are to be refunded
        description: A description of the refund (optional)
        
        Returns: a dict representing a refund, or None if the amount is 0
        """
        p=[("amount",str(amount))]
        if description is not None:
            p+=[("description",description)]
        return self._apicall("https://api.paymill.de/v1/refunds/"+str(tranid),tuple(p))

    def getrefdetails(self, refid):
        """
        Get the details of a refund from its id.
        refid: string Unique id for the refund
        
        Returns: a dict representing a refund
        """
        return self._apicall("https://api.paymill.de/v1/refunds/"+str(refid))
    
    
    def getrefs(self):
        """
        List all stored refunds.
        
        Returns: a dict with a member "data" which is an array of dicts, each representing a refund
        """
        return self._apicall("https://api.paymill.de/v1/refunds/")

    
    
if __name__=="__main__":
    p=Pymill("YOURPRIVATEKEYHERE")
    cc=(p.getcards())["data"][0]["id"]
    print p.getcarddetails(cc)
    #print p.transact(amount=300,card=cc,description="pymilltest")
    
