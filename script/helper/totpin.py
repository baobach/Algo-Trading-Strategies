import pyotp as tp

totp_key = 'LUKCPAFEEHWWZNSNWJMW33TI75OEOEK4'
k=tp.TOTP(totp_key).now()
print(k)