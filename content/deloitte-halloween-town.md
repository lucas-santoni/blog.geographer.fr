---
title: "Deloitte CTF Quals 2019: Halloween Town 🎃"
slug: deloitte-halloween-town
date: 06/11/2019
---

*Halloween Town* 🎃 was a task labelled cryptography and worth 135 points.
It was actually mostly steganography/guessing. The task remained unsolved for
the most part of the competition, until the staff decided to release hints.

![Task Description](/assets/halloween-town/intro.png)

Let's begin with an nmap scan:

```
$ nmap 18.130.113.180
Starting Nmap 7.80 ( https://nmap.org ) at 2019-11-06 16:05 GMT
Nmap scan report for ec2-18-130-113-180.eu-west-2.compute.amazonaws.com (18.130.113.180)
Host is up (0.0038s latency).
Not shown: 990 closed ports
PORT     STATE    SERVICE
22/tcp   open     ssh
25/tcp   filtered smtp
53/tcp   filtered domain
80/tcp   open     http
135/tcp  filtered msrpc
139/tcp  filtered netbios-ssn
445/tcp  filtered microsoft-ds
2000/tcp open     cisco-sccp
5060/tcp open     sip
8008/tcp open     http

Nmap done: 1 IP address (1 host up) scanned in 1.26 seconds
```

So we have access to this front:

![The front](/assets/halloween-town/front.png)

There really is nothing here... Then I downloaded the background image and
found out that the timestamp is weird:

```
root@3853909ffedf:/macOS/halloween# exiftool background.jpg
[...]
Modify Date                     : 1993:10:31 08:02:04
Y Cb Cr Positioning             : Centered
Exif Version                    : 0231
Date/Time Original              : 1993:10:31 08:02:04
Create Date                     : 1993:10:31 08:02:04
[...]
root@3853909ffedf:/macOS/halloween#
```

I got stuck here and stoped working on this challenge. A few hours later, the
staff recommended to use
[StegCracker](https://github.com/Paradoxis/StegCracker). This is mostly a
wrapper around `steghide`, with the ability to perform dictionnary attacks.

Let's try with `rockyou.txt`:

```
root@3853909ffedf:/macOS/halloween# stegcracker background.jpg ../rockyou.txt
StegCracker 2.0.7 - (https://github.com/Paradoxis/StegCracker)
Copyright (c) 2019 - Luke Paris (Paradoxis)

Counting lines in wordlist..
Attacking file 'background.jpg' with wordlist '../rockyou.txt'..
Successfully cracked file with password: halloween
Tried 3099 passwords
Your file has been written to: background.jpg.out
halloween
root@3853909ffedf:/macOS/halloween# cat background.jpg.out
535646564e014502045c4c6d055600474b6b025e015c0603055c014a
root@3853909ffedf:/macOS/halloween#
```

*Note: `steghide` really is a pain to install on macOS because of its
dependencies. An Ubuntu docker is a nice alternative.*

We now have a string. It looks like it's hexadecimal but the output is not
readable. I suspected that the string was xored but `xortool` could not find
anything so I got stuck again.

A few minutes before the end of the CTF, the staff released another
hint: the timestamp of the image is the key. One of my teammates had the idea
to convert the date into a UNIX timestamp. Because of the AM/PM thing, there
are two possible keys: `752097724` and `752054524`. The second is the right one.

We convert it to hexadecimal and xor it with the text we extracted using
`steghide`. The output decodes as:

```
535646564e014502045c4c6d055600474b6b025e015c0603055c014a ^ 373532303534353234
646374667b357030306b795f35633472795f356b336c3337306e357d35
dctf{5p00ky_5c4ry_5k3l370n5}5
```

Final flag: `dctf{5p00ky_5c4ry_5k3l370n5}`.
