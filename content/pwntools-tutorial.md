---
title: Learn pwntools by example
slug: pwntools-tutorial
date: 24/03/2020
description: Learn how to use pwntools, the CTF framework and exploit development library. This article covers the most important pwntools features and teach you how to use them via examples.
---

Now that we are tous confinés, let's try to take advantage of all this free
time dans learn about [pwntools](https://github.com/Gallopsled/pwntools).

> Pwntools is a CTF framework and exploit development library. Written in
> Python, it is designed for rapid prototyping and development, and intended to
> make exploit writing as simple as possible.

The main advantage of pwntools is that is allows you to have a *programmatic
approach* to exploit development. You will not rely on bash one-liners and
other hazardous tricks anymore. Your exploits will now be Python programs that
are easy to maintain, update, and reuse.

The following pwntools features are covered in this article, mostly through
examples and real-world challenges:

* Communication with a process (local and remote)
* Buffer overflow exploitations
* LibC offsets computation
* (Semi-)Automated format string exploitation
* Dealing with other architectures (ARM)
* Using pwntools in the terminal (when a Python script is not needed)

This articles is meant to be read top to bottom but feel free to skip to
a particular section if you are looking for something specific.

*Summary will be added here.*

**Warning! This article is about pwntools itself. You will not be able to
follow allong if you do not know the basics of binary exploitation. If that's
your case, you should take a look at
[this playlist](https://www.youtube.com/playlist?list=PLhixgUqwRTjxglIswKp9mpkfPNfHkzyeN)
by LiveOverflow first.**


## Setting up pwntools

Most of pwntools is implemented in pure Python (version >= 3 recommended) but
the project still has two external dependencies: Binutils, and the Python
development headers.

If you are running Linux, these two dependencies are most likely very easy to
install via the package manager of your distribution.

If you are running macOS, Binutils is hard to install. Well, not *hard*, but
you will have to
[build it from source](https://docs.pwntools.com/en/stable/install/binutils.html#mac-os-x)
and update your `PATH`. You can use pwntools without Binutils but you will not
enjoy all the features the framework has to offer. For instance, you will not
be able to compile shellcodes. Therefore I recommend that you run Pwntools in a
Docker container (an Ubuntu image is a great choice). Windows users should also
consider a Docker container or a virtual machine.

For more information, you should take a look at
[the documentation](https://docs.pwntools.com/en/stable/install.html).

Here is an example Dockerfile, update it so that it suits your needs:

```dockerfile
FROM ubuntu:18.04

RUN \
      apt update && \
      apt install -y \
      python3 \
      python-pip \
      binutils-arm-linux-gnueabi

...
```

*Note: the Binutils have to be installed for any architecture you want to deal
with. The ones for Intel are installed by default but the ones for ARM have to
be installed explicitely (`binutils-arm-linux-gnueabi`) for instance.*

Provided that the Dockerfile is named `Dockerfile` and sits in the current
directory, the image can be built as follows:

```
docker build -t pwn .
```

Run it (the current directory will be mounted to `/host` in the container):

```
docker run -it -v (pwd):/host --rm pwn bash
```

*Note: The `--rm` option allows to automatically remove the container when it
is exited. You may want to get rid of this option if you plan to stop the
container.*

You are now in the container (bash prompt). Feel free to fire a Python 3
interpreter and play with the pwntools API. Also, any Python script that you
create in the host current directory (the one you were in when you launched the
container) will be accessible to the container.


## Getting started

We will begin with some simple local tasks... Our target will be
[this binary]()
I wrote in C and compiled in Linux x64. The source code is
[available here](). The goal is to take advantage of a stack overflow
to overwrite an address.

First, let's import the module:

```python
from pwn import *
```

Most pwntools users import everything in the global scope. Be carefull with
clashes as pwntools export some very common names such as `log` or `args`.
Take a look [at this page](https://docs.pwntools.com/en/stable/globals.html) if
you want an exaustive list of what is imported.

Then, we load the binary, run it and retrieve the output:

```python
target = process(['./target_pwntools'])
output = target.recvall()
print(output)
```

*Note: you can also pass a string to `process`, it will be interpreted as
`argv[0]`. Still, the documentation explicitely requires a `list`.*

Here is what we get:

```
[+] Starting local process './target_pwntools': pid 15
[+] Receiving all data: Done (29B)
[*] Process './target_pwntools' stopped with exit code 1 (pid 15)
b'Please, provide an argument!\n'
```

The `process` constructor allows to wrap a process so that we can interract
with it from our script. For instance, we can use the `recvall` method to
*receive* from the binary.

Right now, it is a local process, but you will soon see that a similar API is
available for remote processes. One of the most powerful feature of pwntools is
that it sees the world through tubes. A tube is something you can talk to. It
can be a local process, a remote process, an SSH connection, a GDB instance...
You will interract with all of them using the same API. This enable you
to develop an exploit locally (where you usually have more debug power) and
then run it remotely with little to no modification.

Let's provide an argument to our target:


```python
target = process(['./target_pwntools', 'ABCDEF'])
```

The output is as expected:

```
[+] Starting local process './target_pwntools': pid 75
[+] Receiving all data: Done (67B)
[*] Process './target_pwntools' stopped with exit code 1 (pid 75)
b'Value of overwrite_me:\t[0xDEADBEEF].\nAwaited value:\t\t[0x44434241].\n'
```

We can observe that `output`
