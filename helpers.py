from __future__ import division
from math import floor

def ip_address(request):
    
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR', None)

    if not ip_address:
        ip_address = request.META.get('REMOTE_ADDR', None)
    else:
        ip_address = ip_address.split(',')[0]
        
    return ip_address

def friendly_num(num):
    """
    return a friendly formatted number
    
    >>> friendly_num(1)
    '1'
    >>> friendly_num(102)
    '102'
    >>> friendly_num(1000)
    '1k'
    >>> friendly_num(10000)
    '10k'
    >>> friendly_num(10200)
    '10.2k'
    >>> friendly_num(100200)
    '100.2k'
    """
    
    if num < 1000:
        return str(num)
            
    hundreds = num % 1000
    thousands = num / 1000
    
    if hundreds > 100:
        return '%0.1fk' % thousands
    else:
        return '%dk' % thousands
    


class NRICValidator(object):
    """
    Validates a Singaporean FIN or NRIC to ensure that it's algorithmically correct
    
    >>> NRICValidator().is_nric_valid('S8944027J')
    True
    >>> NRICValidator().is_fin_valid('G6046409Q')
    True
    >>> NRICValidator().is_nric_valid('S814A299Z')
    False
    >>> NRICValidator().is_fin_valid('G6075119Q')
    False
    
    """
    multiples = [ 2, 7, 6, 5, 4, 3, 2 ]

    def is_nric_valid(self, the_nric):
    
        if not the_nric:
            return False
    
        if len(the_nric) != 9:
            return False;
    
        total = count = 0
        first = the_nric[0]
        last = the_nric[-1];
    
        if first != 'S' and first != 'T':
            return False
    
        try:
            numericNric = int(the_nric[1:-1])
        except ValueError:
            return False
    
        while numericNric != 0:
            total += (numericNric % 10) * self.multiples[len(self.multiples) - (1 + count)]
            
            count += 1
    
            numericNric /= 10
            numericNric = floor(numericNric)
                
        if first == 'S':
            outputs = [ 'J', 'Z', 'I', 'H', 'G', 'F', 'E', 'D', 'C', 'B', 'A' ]
        else:
            outputs = [ 'G', 'F', 'E', 'D', 'C', 'B', 'A', 'J', 'Z', 'I', 'H' ]
    
        return last == outputs[int(total % 11)]
    

    def is_fin_valid (self, fin):
        
        if not fin:
            return False
    
        if len(fin) != 9:
            return False
    
        total = count = 0
        first = fin[0]
        last = fin[-1]
    
        if first != 'F' and first != 'G':
            return False

        try:
            numericNric = int(fin[1:-1])
        except ValueError:
            return False
            
        while numericNric != 0:
            total += (numericNric % 10) * self.multiples[len(self.multiples) - (1 + count)]
            
            count += 1
    
            numericNric /= 10
            numericNric = floor(numericNric)
    
        if first == 'F':
            outputs = [ 'X', 'W', 'U', 'T', 'R', 'Q', 'P', 'N', 'M', 'L', 'K' ]
        else:
            outputs = [ 'R', 'Q', 'P', 'N', 'M', 'L', 'K', 'X', 'W', 'U', 'T' ]
    
        return last == outputs[int(total % 11)]
