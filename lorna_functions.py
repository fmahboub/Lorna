def cfms_to_rating(cfms):
    if cfms > 80:
        return 'Strong Buy'
    elif cfms > 60:
        return 'Buy'
    elif cfms > 40:
        return 'Hold'
    elif cfms > 20:
        return 'Caution'
    elif cfms <= 20:
        return 'Sell Immediately'
    else:
        return '<NA>'