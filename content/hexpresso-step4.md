---
title: Hexpresso FIC Quals 2019: Step 4
slug: hexpresso-fic-4
date: 19/12/2019 04
---

The fourth step is a reverse engineering challenge.

![Introduction](/assets/hexpresso-fic-quals/step4/intro.png)

We are given an archive that contains a Linux binary, which is a fake
ransomware, and a file that has been encrypted, that we must recover.

Let's take a look at the binary:

```
$ file wannafic
wannafic: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=97354f92f87502594330507adef22eca2765dd76, for GNU/Linux 3.2.0, stripped
```

It is stripped. However, no obfuscation or anti-debug so it is very
readable in Ghidra.

The first step is to find the address of `main`. We know that it is the first
argument passed to `__libc_start_main`, called by `entry`:

![Entry](/assets/hexpresso-fic-quals/step4/entry.png)

We now know that `main` is `FUN_00101570`:

![Main](/assets/hexpresso-fic-quals/step4/main.png)

`main` iterates over the file paths passed as parameters and calls
`FUN_001014f3`:

![Encrypt File](/assets/hexpresso-fic-quals/step4/encrypt_file.png)

This function retrieves the current time via `time(NULL)` and call the actual
encryption routine (`FUN_00101220`). Let's see:

![Routine](/assets/hexpresso-fic-quals/step4/routine.png)

Nothing special, it is a basically a XOR. The key is generated from the
current time and the name of the file to be encrypted.

Let's recap what we know:

* For a given key, the encryption and decryption routines are the same (as it is
XOR-based)
* The key is derived from the current time, and the name of the file before
it is encrypted
* We have a crypted file

Let's see at what time the crypted file has been generated:

```
$ stat flag.txt.crypt
16777220 16551658 -rw-r--r-- 1 geographer staff 0 2912 "Dec 12 13:37:48 2019" "Dec 12 13:37:42 2019" "Dec 19 17:45:01 2019" "Dec 12 13:37:42 2019" 4096 8 0 flag.txt.crypt
```

`Dec 12 13:37:42 2019` is a fairly explicit date. Its original name is
`flag.txt` as the crypter adds `.crypt` at the end of the filename after
encryption. We have all we need to decrypt the file.

We could re-implement the routine in C from Ghidra's or IDA's decompilation
output but it is faster to re-use the crypter itself, as the algorithm is
symmetrical. We only need to force the system date to be `Dec 12 13:37:42
2019`, and rename the crypted file to `flag.txt` so that we generate the same
key.

In order not to mess with the actual system time, and also get the same
`(s)rand` implementation, we can use [Vagrant](https://www.vagrantup.com/).
Ubuntu worked for me:

```ruby
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/xenial64"
  config.vm.define :random
end
```

Once inside the box:

```
$ mv flag.txt.crypt flag.txt
$ sudo date -s "Dec 12 13:37:42 2019" && ./wannafic flag.txt
Thu Dec 12 13:37:42 UTC 2019

 ▄█     █▄     ▄████████ ███▄▄▄▄   ███▄▄▄▄      ▄████████
███     ███   ███    ███ ███▀▀▀██▄ ███▀▀▀██▄   ███    ███
███     ███   ███    ███ ███   ███ ███   ███   ███    ███
███     ███   ███    ███ ███   ███ ███   ███   ███    ███
███     ███ ▀███████████ ███   ███ ███   ███ ▀███████████
███     ███   ███    ███ ███   ███ ███   ███   ███    ███
███ ▄█▄ ███   ███    ███ ███   ███ ███   ███   ███    ███
 ▀███▀███▀    ███    █▀   ▀█   █▀   ▀█   █▀    ███    █▀
                        FIC2020
                  ▄████████  ▄█   ▄████████
                 ███    ███ ███  ███    ███
                 ███    █▀  ███▌ ███    █▀
                ▄███▄▄▄     ███▌ ███
               ▀▀███▀▀▀     ███▌ ███
                 ███        ███  ███    █▄
                 ███        ███  ███    ███
                 ███        █▀   ████████▀

[*] Encrypting flag.txt
[*] ts : 1576157862
[*] Writing to flag.txt.crypt
[*] Done !

$ cat flag.txt.crypt
x>`oaNFDTF}O]
```

It does not seem to work... And the decrypted file is much smaller than
the encrypted one.

I spent some more time in Ghidra and noticed something in the (en/de)cryption
routine:

```c
while( true ) {
  iVar2 = fgetc(pFParm1);
  if ((byte)iVar2 == 0xff) break;
  // ...
}
```

The original file is guaranteed not to contain any `0xff`. However, the
encrypted file definitely contains some. Let's replace (and not remove as it
will invalidate the generated key, the total number of bytes to (en/de)crypt
must be the same) them and try again:

```
$ mv flag.txt.crypt flag.txt
$ sed -i 's/\xff/\x00/g' flag.txt
$ sudo date -s "Dec 12 12:37:42 2019" && ./wannafic flag.txt
[same output as before]
$ cat flag.txt.crypt
```

*Note: after a few tries, I forced the system time to 12:37, instead of 13:37.
I don't really know why, maybe some timezone issue because I live in France.*

And...

```
 ██░ ██ ▓█████ ▒██   █▒ ██▓██   ██▀███  ▓█████   ██████   ██████  ▒█████      █     █░ ▄▄▄        ██████     ██░ ██ ▓█████  ██▀███  ▓█████
▓██░ ██▒▓█   ▀ ▒▒ █ █ ▒░▓██░  ██▒▓██ ▒ ██▒▓█   ▀ ▒██    ▒ ▒██    ▒ ▒██▒  ██▒   ▓█░ █ ░█░▒████▄    ▒██    ▒    ▓██░ ██▒▓█   ▀ ▓██ ▒ ██▒▓█   ▀
▒██▀▀██░▒███   ░░  █  ▓██░ ██▓▒▓██ ░▄█ ▒▒███   ░ ▓██▄   ░ ▓██▄   ▒██░  ██▒   ▒█░ █ ░█ ▒██  ▀█▄  ░ ▓██▄      ▒██▀▀██░▒███   ▓██ ░▄█ ▒▒███
░▓█ ░██ ▒▓█  ▄    █ █ ▒ ▒██▄█▓▒ ▒▒██▀▀█▄  ▒▓█    ▒   ██▒  ▒   ██▒▒██   ██░   ░█░ █ ░█ ░██▄▄▄▄██   ▒   ██▒   ░▓█ ░██ ▒▓█  ▄ ▒██▀▀█▄  ▒▓█  ▄
░▓█▒░██▓░▒████▒▒██▒ ▒██▒▒██▒ ░  ░░██▓ ▒██▒░▒████▒▒██████▒▒▒██████▒▒░ ████▓▒░   ░░██▒██▓  ▓█   ▓██▒▒██████▒▒   ░▓█▒░██▓░▒████▒░██▓ ▒██▒░▒███▒
 ▒ ░░▒░▒░░ ▒░ ░▒▒ ░ ░▓ ░▒▓▒░ ░  ░░ ▒▓ ░▒▓░░░ ▒  ░▒ ▒▓▒ ▒ ░▒ ▒▓▒ ▒ ░░ ▒░▒░▒░    ░░▒ ▒   ▒▒   ▓▒█░▒ ▒▓▒ ▒ ░    ▒ ░░▒░▒░░ ▒░ ░░ ▒▓ ░▒▓░░░ ▒░ ░
 ▒ ░▒░ ░ ░ ░  ░░   ░▒ ░░▒ ░       ░▒ ░ ▒░ ░ ░  ░░ ░▒  ░ ░░ ░▒  ░ ░  ░ ▒ ▒░      ▒ ░ ░    ▒  ▒▒ ░░▒  ░ ░    ▒ ░▒░ ░ ░ ░  ░  ░▒ ░ ▒░ ░ ░  ░
 ░  ░░ ░   ░    ░    ░  ░░        ░░   ░    ░   ░  ░  ░  ░  ░  ░  ░ ░ ░ ▒       ░   ░    ░   ▒   ░  ░  ░      ░  ░░ ░   ░     ░░   ░    ░
 ░  ░  ░   ░  ░ ░    ░             ░        ░  ░      ░        ░      ░ ░         ░          ░  ░      ░      ░  ░  ░   ░  ░   ░        ░  ░


Well done buddy !!!!
Next step : https://ctf.hexpresso.fr/6bd1d24ab3aa08784f868a533bcdc215
```

[Click here](/posts/hexpresso-fic-5) for the next step!