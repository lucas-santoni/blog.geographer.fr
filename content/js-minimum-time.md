---
title: [FRENCH] JavaScript : durée minimum à l'exécution d'une fonction asynchrone
slug: js-minimum-time
date: 12/10/2018
---

Un ami m'a demandé si il était possible de forcer une fonction asynchrone à
mettre au moins une certaine période de temps à s'exécuter. Par fonction
asynchrone, j'entends fonction retounant une `Promise`.

Commençons par écrire une fonction asynchrone de test :

```js
const request = ms => new Promise(s => setTimeout(s, ms));
```

Cette fonction simule par exemple une requête HTTP. On veut que cette fonction
mette, disons, au moins 3 secondes à retourner son résultat. Le temps entre
l'appel de la fonction et la résolution de la promesse renvoyée est donc
compris entre :

  * 3 secondes au minimum
  * une durée maximale inconnue, correspondant au temps qu'il faut à
  la `Promise` retournée pour être résolue

On va wrapper l'appel à la fonction `request` pour faire notre cuisine.

La durée maximale se gêre facilement, c'est simplement un `.then()`/`.catch()`
classique :

```js
const atLeast3seconds = timeOfRequest => new Promise((s, f) => {
  const p = request(timeOfRequest);

  p
    .then(r => s(r))
    .catch(e => f(e));
});
```

_**Note** : pour faciliter les tests, je prends le temps d'exécution de la
fonction `request` en paramètre._

On lance la fonction, on récupère la promesse associée puis on la synchronise
aussitôt avec la promesse de notre wrapper.

Par exemple :

```js
atLeast3Seconds(process.argv[2] || 1000)
  .then(() => console.log('Done !'))
  .catch(e => console.error(e));
```

Donne :

```
tmp time node script.js 4000
Done !
        4.08 real         0.06 user         0.01 sys
tmp time node script.js 500
Done !
        0.59 real         0.07 user         0.01 sys
```

Le problème est que, du coup, notre wrapper peut retourner en moins de 3
secondes... Pour régler ce problème, on va utiliser la fonction `setTimeout`
afin de ne pas synchroniser aussitôt la promesse retournée mais au bout
de trois secondes. Ainsi :

  1. On lance la fonction `request` et on récupère la promesse associée
  2. On attend trois secondes
  3. On synchronise la promesse avec celle de notre wrapper

```js
const atLeast3Seconds = timeOfRequest => new Promise((s, f) => {
  const p = request(timeOfRequest);

  setTimeout(() => {
    p
      .then(r => s(r))
      .catch(e => f(e));
  }, 3000);
});
```

Donne :

```
tmp time node script.js 4000
Done !
        4.09 real         0.07 user         0.01 sys
tmp time node script.js 500
Done !
        3.09 real         0.07 user         0.01 sys
```

Cool ! On rend la fonction générique en prenant la fonction à wrapper
ainsi que le délai en paramètre et c'est fini :

```js
const atLeast = (fct, ms) => new Promise((s, f) => {
  const p = fct();

  setTimeout(() => {
    p
      .then(r => s(r))
      .catch(e => f(e));
  }, ms);
});
```
