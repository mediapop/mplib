
def ip_address(request):
    
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR', None)

    if not ip_address:
        ip_address = request.META.get('REMOTE_ADDR', None)
    else:
        ip_address = ip_address.split(',')[0]
        
    return ip_address