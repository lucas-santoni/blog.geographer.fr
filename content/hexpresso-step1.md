---
title: Hexpresso FIC Quals 2019: Step 1
slug: hexpresso-fic-1
date: 19/12/2019 01
---

The first step is a JavaScript challenge.

Here is the source code that is embedded into the page:

```javascript
const play = () => {
  var game = new Array(
    116, 228, 203, 270, 334, 382, 354, 417, 485, 548, 586, 673, 658, 761, 801,
    797, 788, 850, 879, 894, 959, 1059, 1071, 1140, 1207, 1226, 1258, 1305,
    1376, 1385, 1431, 1515
  );

  const u_u = "CTF.By.HexpressoCTF.By.Hexpresso";
  const flag = document.getElementById("flag").value;

  for (i = 0; i < u_u.length; i++) {
    if (u_u.charCodeAt(i) + flag.charCodeAt(i) + i * 42 != game[i]) {
      alert("NOPE");
      return;
    }
  }

  // Good j0b
  alert("WELL DONE!");

  document.location.replace(
    document.location.protocol +
      "//" +
      document.location.hostname +
      "/" +
      flag
  );
};

/**
 ** Thanks all <3
 ** @HexpressoCTF
 **
 ** The next step is here : https://ctf.hexpresso.fr/{p_p}
 **/
```

This line is important:

```javascript
if (u_u.charCodeAt(i) + flag.charCodeAt(i) + i * 42 != game[i]) {
```

Its a simple equation (pseudocode):

```javascript
u_u[i] + flag[i] + i * 42 = game[i]
```

`u_u` and `game` are hardcoded and given to us. What we are looking for is
`flag`. So:

```javascript
flag[i] = game[i] - u_u[i] - i * 42;
```

Here is my JavaScript solution:

``` javascript
const play = () => {
  const game = new Array(
    116, 228, 203, 270, 334, 382, 354, 417, 485, 548, 586, 673, 658, 761, 801,
    797, 788, 850, 879, 894, 959, 1059, 1071, 1140, 1207, 1226, 1258, 1305, 1376,
    1385, 1431, 1515
  );

  const u_u = "CTF.By.HexpressoCTF.By.Hexpresso";

  let r = "";
  for (const i in u_u) {
    r += String.fromCharCode(game[i] - u_u.charCodeAt(i) - i * 42);
  }

  return r;
}

console.log(play());
```

It outputs the flag: `1f1bd383026a5db8145258efb869c48f`. [Click here](/hexpresso-fic-2) for the next step!