---
title: "Santhacklaus 2019: Christmas Locker"
slug: santa-christmas-locker
date: 23/12/2019
---

**Before we start!** This post is authored by [@pwnh4](https://twitter.com/pwnh4).
I'm really proud to have him for this guest post as he started computer security
only a few months ago with my [2019 Piscine](https://blog.geographer.fr/posts/piscine-poc-2019)
but already performs very well in CTF. Go follow him!

***

*Christmas Locker* is a cryptography challenge of the Santhacklaus 2019 CTF.

![Intro](/assets/santa/locker/chall.png)

We get two files:

```
➜  unzip files.zip
Archive:  files.zip
 extracting: secret.pdf.santa        
  inflating: shift_encrypt.py
```

## What's up?

We can easily understand that we need to decode the `.pdf.santa` file into
its `.pdf` equivalent by reversing the `shift_encrypt.py` encryption. Let's
see what's in this script:

```python
import sys

lfsr_size = 32
lfsr_feeback = 0X100400007

def binarraytoint(bitlist):
	out = 0
	for bit in bitlist:
		out = (out << 1) | bit
	return out

def hamming_weigth(x):
	c = 0
	while(x):
		c += x % 2
		x = x >> 1
	return c

class shift_encrypt():
	def __init__(self,state,lfsr_size,feedback):
		self.state = state
		self.lfsr_size = lfsr_size
		self.feedback = feedback

	def get_key_stream(self,stream_size):
		stream = []
		for i in range(stream_size):
			newbit = hamming_weigth (self.state & self.feedback) % 2
			stream.append(newbit)
			newbit = newbit << self.lfsr_size - 1
			self.state = (self.state >> 1) | newbit
		return stream
	
def encrypt_byte(stream, b):
	k = binarraytoint(stream)
	b = int.from_bytes(b,"big")
	c = b ^ k
	c = c.to_bytes(1, byteorder='big')
	return c 

if (len(sys.argv) != 3):
		print ("Usage: shift_encrypt <key> <file>")
		exit(-1)
	
state = int(sys.argv[1],16)

se = shift_encrypt(state,lfsr_size,lfsr_feeback)
	
try:
	input = open(sys.argv[2],"rb")
	output = open(sys.argv[2]+".santa","wb")
	
	while True:
		cleartext = input.read(1)
		if cleartext:
			stream = se.get_key_stream(8)
			c = encrypt_byte(stream,cleartext)	
			output.write(c)
		else:
			break	

finally:
	input.close()
	output.close()
```

We can see that the encryption process uses an LFSR logic.

An LFSR (for *__L__inear __F__eedback __S__hift __R__egisters*) can, in this
implementation, be described as :

* A 32 bits register (see `lfsr_size` variable). The choice of 32 bits is convenient because it is the size of an integer.
* Its initial state (initial value of the 32 bits), as defined by the user in `argv[1]`
* A bunch of operations are made with the state of the LFSR (`self.state = (self.state >> 1) | newbit`)
* The output of those operations become the next state of the register and is used in the next cycles

Here, each state is used to generate a byte, called stream (with the method
`get_key_stream`) that will then be used to XOR a byte of the input file.
This is how the PDF file was encrypted.

Sexy representation of the encryption process:

```
initial_state -> process -> update state -> process -> update state -> ...
                    |                          | 
                    |-> generated stream byte  |-> generated stream byte 
                           |                          |
                           |-> XOR with input         |-> XOR with input
```

## Unciphering

We know that the encrypted file is a PDF. So we know that this file
starts with the bytes `%PDF`. We can easily find the first generated stream
by XORing the byte `%` with the first encrypted byte.

The issue here is that there are multiple initial states of the LFSR that can
generate this initial stream.

So what we can do is try every possibilities of initial states which generate
the correct stream for the first 4 bytes of the pdf. If an initial state can
be valid during four cycles, we can assume that it will be valid for all the
rest of the file.

```python
def get_original_state(encrypted, checking=0, state=None):
  """
  encrypted : encrypted files as bytes array
  checking  : current evaluated byte
  state     : initial state of the current cycle
  """
  first_pdf_bytes = [0x25, 0x50, 0x44, 0x46]
  if checking == len(first_pdf_bytes):
      return True

  # get the stream used to XOR the CHECKINGth byte
  orig_intstream = first_pdf_bytes[checking] ^ encrypted[checking]
  orig_stream = []
  for i in range(8):
      orig_stream.append(orig_intstream & 1)
      orig_intstream = orig_intstream >> 1
  orig_stream = orig_stream[::-1]

  if not state:
      # we iterate over all possible first state values
      for x in range(0, 99999999):
          STATE = x
          stream = []
          for i in range(8):
              newbit = hamming_weigth(x & 0X100400007) % 2
              stream.append(newbit)
              newbit = newbit << 32 - 1
              x = (x >> 1) | newbit
          if stream == orig_stream:
              # check recursively if the current initial state is valid for the next
              if get_original_state(encrypted, checking + 1, x):
                  print("[+] Original state was", STATE)
  else:
      x = state
      stream = []
      for i in range(8):
          newbit = hamming_weigth(x & 0X100400007) % 2
          stream.append(newbit)
          newbit = newbit << 32 - 1
          x = (x >> 1) | newbit
      if stream == orig_stream:
          # if arrive here, the intermediate cycle is validated and try to validate next cycle
          return get_original_state(encrypted, checking + 1, x)
  return False
```

Which outputs:

```
[+] Original state was 5929497
```

We can now launch the `shift_encrypt.py` script with this value and get the
original PDF file, in which we can see :

![FLAG](/assets/santa/locker/flag.png)
