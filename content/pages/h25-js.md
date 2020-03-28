---
title: Cours de JavaScript (stream h25)
slug: h25-js
---

*Pourquoi ce document ?* Il s'agit d'une reprise écrite du cours j'ai
pu donner pendant le stream de 25 heures organisé par h25 à l'occasion
du confinement provoqué par l'épidémie de Coronavirus qui frappe
actuellement l'Europe.

## Objectif

Ce cours a pour objectif de présenter les aspects essentiels du langage
JavaScript, en particulier ceux utiles au joueur de *Capture The Flag*
(CTF). Nous verrons :

-   Comment gérer une épreuve tout ou partie écrite en JavaScript
-   Comment effectuer (plus efficacement?) des taches de *scripting* qui
    sont traditionellement réservées à Python ou Bash

Aucune connaissance du langage JavaScript n'est requise.

**Attention ! On ne parlera pas ici de XSS ou autres vulnérabilités client.**

## Mise en bouche

JavaScript est un langage qui fait débat, toujours très controversé.  Plusieurs
enquêtes, notamment [celles de GitHub](https://octoverse.github.com/) (qui
vient d'ailleurs d'acquérir `npm`), le placent en tête des langages les plus
utilisés au monde (on peut débattre sur ce que *plus utilisé* signifie, certes)
et il est aujourd'hui absolument partout : dans nos navigateurs, dans nos
serveurs web, dans nos appareils mobiles, dans nos applications de bureau...

Mais il est aussi dans nos CTFs ! Et on le retrouve dans plusieurs
catégories : web, bien sur, mais aussi crypto, forensique, malware,
mobile, etc. Le JavaScript peut bien sur être le sujet de l'épreuve en
elle-même, mais il peut également être simplement le moyen d'intéragir
avec l'épreuve (comme on l'a vu lors [du dernier stream
H25](https://www.youtube.com/watch?v=tzFHvqaYnoM)).

Le problème, c'est que beaucoup de joueurs de CTFs ne connaissent pas
*vraiment* le JavaScript. C'est à dire : beaucoup de joueurs sont
capables d'inférer ce que fait un bout de code en se ratachant à des
mots clés, à des noms de méthode, ou à des constructions de
programmation orientée objet qui leurs sont familiers parce que
similaires à ce qui se fait dans d'autres langages. Le bat blesse quand
il s'agit d'écrire du code, et plus seulement en lire. Ou bien,
lorsque le code étudié présente des fonctionnalités avancées de
JavaScript, en particulier celles relatives à la programmation
asynchrone.

## Fondamentaux

Commençons par l'étude d'un bout de code qui va nous permettre de
clarifier certains aspects simples, mais pourtant souvent sources de
confusion, du langage...

```javascript
// Quelques notions de JavaScript
// D'autres constructions utiles sont présentées plus tard

// Il n'y a pas de fonction main
// Chaque fichier est un script indépendant, évalué comme tel
// Des fonctionnalités d'importation permettent de diviser les sources
// en plusieurs fichiers

// Le mot clé var permet d'associer un identifiant (le "nom" de la variable)
// a une valeur
var name = 'some_value';

// Il est possible de réaffecter cet identifiant
// On peut utiliser des guillemets simples, ou doubles
// Attention, var est très souvent banni, au profit de let et const
name = "some 'other' value";
name = 'some "other" value';
name = 'some \'other\' value';

// On peut aussi utiliser l'accent grave pour profiter des "template literals"
// (en français : littéraux de gabarits, quel plaisir) et donc de
// fonctionnalités d'interpolation
// Les accents graves permettent également de faire du multi-lignes
name = `I am ${Math.floor(Math.random() * 10)} years old!`;

// Le mot clé let est une autre manière d'associer un identifiant à une valeur
// Tout comme var, on peut réaffecter l'identifiant
// En revanche, un identifiant déclaré avec let a une durée de vie
// limitée : le bloc courant
let other_name = name;
other_name = "my own name";

// Finalement, le mot clé const permet également d'associer un idenfiant
// à une valeur
// Grosse différence : un idenfiant déclaré avec const ne peut être réaffecté
const constant_name = "this is so constant";

// !! Ne fonctionne pas
// constant_name = "nop, sorry";

// Attention, seul l'identifiant est garanti constant
// La valeur ne n'est pas
const some_object = {
    prop_one: 'value one',
    prop_two: 'value two'
};

// Aucun problème : on met à jour la valeur et non l'identifiant
some_object.prop_two = 'value twotwo';
some_object.prop_three = 'value three';

// Les ; en fin d'instruction sont obligatoires (d'après le standard)
// Mais, dans de nombreux cas, un code sans ; pourra être correctement exécuté
// parce que l'interpréteur peut les ajouter à la volée

// Le mot clé function permet de déclarer une fonction
function some_function(some_argument) {
    // Si un indentifiant a été déclaré mais n'a pas été initialisé,
    // sa valeur est undefined
    if (some_argument !== undefined) {
        console.log(`I got an argument: ${some_argument}!`);
    }
}

// Ne génère aucune erreur, some_argument aura simplement une valeur de
// undefined au sein de la fonction some_function
some_function();

// JavaScript dispose d'un système de typage dynamique
some_function("some string");
some_function(1337);

// Les fonctions sont des objets de première classe
// (en anglais : "first class citizen")
// On peut donc les passer comme argument, les utiliser comme
// valeur de retour, etc
some_function(some_function);

// Il existe une autre syntaxe permettant de déclarer une
// fonction : la fat arrow
// On parle aussi de fonctions fléchées
// Ces fonctions introduisent bien un nouveau bloc (scope) mais pas
// de this ou de super
a => console.log(a);
(a, b) => a + b;
(a, b, c) => {
    let d = a + b;
    return d * c;
}

// Toutes les fonctions déclarées ci-dessus sont anonymes : ce sont des valeurs
// qui n'ont pas été associées à un identifiant
// A l'instar de var, function est parfois banni au profit de
// la construction suivante
const my_function = (arg1, arg2) => {
    console.log(arg1, arg2);
    return arg1 * arg2;
};

// Les tableaux
const some_array = [1, 2, 3, 4];
some_array.push('hello'); // Le tableau n'est pas fortement typé

// Ou bien, via constructeur
const another_array = new Array(); // Renvoie []

// Contrôler la longueur initiale
const more_array = new Array(5); // Renvoie un tableau de 5 éléments vides

// Attention, si plus de deux arguments, les arguments deviennent des valeurs
const awesome_array = new Array(5, 6, 7); // [5, 6, 7]

// Les objets
// JSON : JavaScript Object Notation
const my_object = {
    property_one: 42,
    property_two: 'hello',
    method_one: () => 'hello from method_one',
    method_two: function () {
        return this.property_one;
    }
};

// Accès par .
console.log(my_object.property_one);

// Accès par [] (genre dictionnaire)
console.log(my_object['method_one']);
const attr = 'method_one'; console.log(my_object[attr]);

// Boucle while
let i = 0;
while (i < 10) {
    console.log(i++); // on a aussi --i, ++i et i--
}

// Boucle for
const arr = ['hello', 'les', 'amis'];

// Simple
for (let i = 0; i < arr.length; i++) {
    console.log(arr[i]);
}

// Accès aux valeurs
// On remarque le const : un nouveau scope est introduit à chaque tour
for (const i of arr) {
    console.log(i);
}

// Accès aux indices
// Même principe pour le const
for (const i in arr) {
    console.log(i);
}
```

On peut exécuter du JavaScript dans différents environnements. Le plus évident
est un navigateur WEB : on navigue sur un site web qui utilise du JavaScript.
Mais on peut aussi exécuter du JavaScript en dehors du navigateur, par exemple
à l'aide de [Node.js](https://nodejs.org/en/about/).

Si on part du principe que deux environnements d'exécution implémentent
la même version du standard, tous les éléments de syntaxe que l'on
vient d'étudier seront valables et produiront des résultats identiques
dans les deux environnement.

En revanche, le contexte sera différent. Un bout de code JavaScript
exécuté dans le navigateur peut accéder à l'objet `document`, qui
représente la page web. Node.js ne peut accéder à cet objet car il ne
fait pas sens dans son contexte. En revanche, Node.js fourni le module
`fs` qui est une API pour intéragir avec le système de fichier. Le
navigateur ne propose pas cette API, car il n'a pas accès au système de
fichier (c'est [en train
d'évoluer](https://developer.mozilla.org/en-US/docs/Web/API/FileSystem)
ceci dit).

En fonction de l'environnement, les connaissances requises pour gêrer
une épreuve peuvent être très différentes. Une épreuve qui se passe dans
le navigateur pourra demander d'être à l'aise avec les manipulations
du DOM tandis qu'une épreuve serveur demandera de connaitre le
fonctionnement de la librairie [Express](https://expressjs.com/fr/).

## Constructions utiles

Maintenant que nous avons les bases, voyons quelques constructions qui
reviennent fréquemment en CTF...

### Manipulations ASCII

*Bout de code adapté de l'étape 1 des Hexpresso FIC Quals 2019.
[Write-up complet disponible
ici.](/hexpresso-fic-1)*

```javascript
for (i = 0; i < some_string.length; i++) {
    if (some_string.charCodeAt(i) + flag.charCodeAt(i) + i * 42 != some_array[i]) {
        alert("NOPE");
        return;
    }
}
```

On remarque:

-   La méthode `charCodeAt(i)` qui, lorsque appliquée sur une chaine de
    caractère, nous renvoie la valeur numérique du i<sup>ème</sup> caractère de
    la chaine.
-   La fonction `alert`, uniquement disponible dans le navigateur, qui
    permet de rapidement afficher un message. La fonction est utile pour
    du débogage car elle bloque entièrement le flux d'exécution.
-   Quelques opérateurs comme `+` et `*`, ici appliqués à des nombres.
    D'autres existent, y compris les opérateurs
    [bits à bits](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Bitwise_Operators).

Voyons un code solution :

```javascript
let r = "";
for (const i in flag) {
    r += String.fromCharCode(some_array[i] - some_string.charCodeAt(i) - i * 42);
}
```

On remarque alors que `String.fromCharCode(i)` (méthode statique) permet
l'opération inverse de `charCodeAt(i)`. On obtient alors le caractère
(attention, il s'agit en fait d'une chaine de caractères de longueur
1) correspondant au nombre `i`.

Utilisateurs de Python, attention, JavaScript permet l'opérateur `+`
sur des chaines de caractère mais il ne permet pas la multiplication. On
utilise pour ça la méthode statique `String.repeat()`.

On commence à comprendre que JavaScript fourni de très nombreux
utilitaires. Le langage dispose également d'un écosystème imposant. Il
est très rare de ne pas trouver une dépendance permettant de répondre à
son problème.

### Minification

Beaucoup d'épreuves présentent de la minification. Le premier cas
d'usage en JavaScript est certainement la réduction de la taille du
code. Parce que le code JavaScript client est téléchargé depuis un
serveur WEB, on cherche à réduire la taille de ce code afin d'accélérer
sa récupération.

*Note : dans la grande majorité des cas, un code minifié ne s'exécute
pas plus rapidement qu'un code non-minifié. Il est simplement plus
rapide à télécharger.*

Dans le contexte d'un CTF, la minification devient une forme
d'ofuscation. Le code suivant:

```javascript
const obj = {
    firstname: 'Geo',
    lastname: 'Le Berlingot'
};

function getFullName(person) {
    return person.firstname + ' ' + person.lastname
}

console.log(getFullName(obj));
```

Devient, une fois minifié avec [JavaScript Minifier](https://javascript-minifier.com/) :

```javascript
function getFullName(e){return e.firstname+" "+e.lastname}const obj={firstname:"Geo",lastname:"Le Berlingot"}
console.log(getFullName(obj))
```

On utilise alors le minimum de caractères possibles. Les espaces sont
retirés, les noms sont manglés... Mais ce code est tout à fait lisible
et on peut très facilement retomber proche du code initiale en utilisant
un outil tel que
[l'outil de formatage de Chrome](https://developers.google.com/web/tools/chrome-devtools/javascript/reference#format).

Mais il existe aussi des outils proposant une ofuscation beaucoup plus
franche. Par exemple, avec [JavaScript Obfucator](https://obfuscator.io/), notre code initiale devient:

```javascript
const _0x1616=['lastname','firstname','Geo','Le\x20Berlingot'];(function(_0x177eb0,_0x1616a6){const _0x1e9abe=function(_0x204014){while(--_0x204014){_0x177eb0['push'](_0x177eb0['shift']());}};_0x1e9abe(++_0x1616a6);}(_0x1616,0xc6));const _0x1e9a=function(_0x177eb0,_0x1616a6){_0x177eb0=_0x177eb0-0x0;let _0x1e9abe=_0x1616[_0x177eb0];return _0x1e9abe;};const obj={'firstname':_0x1e9a('0x0'),'lastname':_0x1e9a('0x1')};function getFullName(_0xb6014e){return _0xb6014e[_0x1e9a('0x3')]+'\x20'+_0xb6014e[_0x1e9a('0x2')];}console['log'](getFullName(obj));
```

Et on a quelque chose qui est déjà beaucoup moins lisible. La
méthodologie varie en fonction du temps que l'on peut investir et le
type d'obfuscation mais dans le cas général, on peut commencer par
faire passer le code dans un outil de déofuscation tel que
[de4js](https://lelinhtinh.github.io/de4js/) et ensuite terminer à la
main. On va chercher principalement à :

-   Renommer les noms de variables et functions
-   Extraire les différents éléments, notamment les chaines de
    caractères, que les ofuscateurs ont tendance à regrouper dans des
    tableaux
-   Retirer le code inutile

J'avais déjà évoqué l'ofuscation en JavaScript dans [ce
writeup](https://blog.geographer.fr/so-stealthy) d'une épreuve des
qualifications de la Nuit Du Hack 2018.

### Encodages

JavaScript donne accès, même sans dépendances, à plusieurs encodages dont les
challenges ont tendance à abuser. Si on ne les connait pas, ils peuvent donner
l'impression qu'on doit gêrer un chiffrement complexe ou une bizarrerie
JavaScript alors qu'un simple appel de fonction suffit. On a :

- [`unescape()`](https://developer.mozilla.org/fr/docs/Web/JavaScript/Reference/Objets_globaux/unescape) pour gêrer les séquences hexadécimales
- [`decodeURI()`](https://developer.mozilla.org/fr/docs/Web/JavaScript/Reference/Objets_globaux/decodeURI), semblable à `unescape()`
- [base64](https://developer.mozilla.org/fr/docs/Web/API/WindowBase64/D%C3%A9coder_encoder_en_base64)
- [API Buffer](https://nodejs.org/api/buffer.html), qui expose plusieurs fonctions intéressantes, notamment `toString` et `from`

Attention également à la fonction [`eval`](https://developer.mozilla.org/fr/docs/Web/JavaScript/Reference/Objets_globaux/eval).

### Quelques writeups

- [JS SAFE 2.0 - Google CTF 2018, par LiveOverflow](https://www.youtube.com/watch?v=8yWUaqEcXr4)
- [JS Kiddie - picoCTF 2019, par radekk](https://medium.com/@radekk/picoctf-2019-writeup-for-js-kiddie-7af4f0a20838)
- [Javascript Obfusqué - Qualification SIGSEGV1, par Jean MARSAULT](https://www.securityinsider-wavestone.com/2018/10/ctf-quals-rtfm.html)
- [Web 2.0 - Flare-On 5](https://blog.attify.com/flare-on-5-writeup-part3/)

## Concurrence

JavaScript inplémente une boucle d'évènement (en anglais: *event
loop*), qui l'ammène à ne pas être bloquant. En Python, lorsqu'on fait
une requête HTTP avec le module `request`, il est impossible (du moins,
sans efforts) d'exécuter plus de code pendant que cette requête a lieu.
On dit alors que l'appel Python est bloquant, car il monopolise le
*runtime* et ne \"rend pas la main\".

### Callbacks

L'approche la plus simpliste est celle du *callback*. La fonction
permettant de faire une requête HTTP prend alors un autre paramètre :
une fonction, qui sera appelée lorsque le résultat sera disponible. Ce
callback reçoit en paramètre le (ou les, y compris les erreurs) résultat
de l'opération asynchrone.

```javascript
const request = require('request');

request.get('https://geographer.fr/', (err, result) => {
    if (err) {
        console.error(err);
        return;
    }

    console.log(result.body.slice(0, 500));
});

console.log('Where am I?');
```

On remarque que la méthode `request.get` retourne immédiatement. Le flux
d'exécution n'est donc pas bloqué pendant la requête HTTP, on peut
continuer d'exécuter le code qui se trouve plus bas.

Le callback, qui est ici une fonction anonyme, sera appelé une fois que
le résultat de l'opération asynchrone sera disponible. Le runtime fera
alors une pause dans l'exécution de son fil \"principal\" afin
d'exécuter le callback.

```javascript
const request = require('request');

console.log('BEFORE request call!');

request.get('https://geographer.fr/', (err, result) => {
    console.log('START of callback!');

    if (err) {
        console.error(err);
        return;
    }

    console.log(`Body has a length of ${result.body.length}.`);
    console.log('END of callback!');
});

console.log('AFTER request call!');
```

Il est très rare de voir des callbacks aujourd'hui en raison du
*callback hell*, cette situation où on se retrouve à imbriquer plusieurs
callbacks, ce qui rend le code très peu lisible. Imaginons un code
suivant : requête HTTP, sauvegarde du résultat dans un fichier texte,
puis duplication de ce fichier. Le code aurait cette allure :

```javascript
const request = require('request');
const fs = require('fs');

request.get('https://geographer.fr/', (e, r) => {
    if (e) {
        console.error(e);
        return;
    }

    fs.writeFile('/tmp/output.txt', r.body, (e, r) => {
        if (e) {
            console.error(e);
            return;
        }

        fs.copyFile('/tmp/output.txt', '/tmp/output_copy.txt', (e, r) => {
            if (e) {
                console.error(e);
                return;
            }

            console.log('Work is done!');
        });
    });
});
```

Quel plaisir... Il est trop difficile de suivre le fil de ce code, sans
compter qu'il vire dangereusement à droite. Voyons comment les
promesses peuvent nous aider !

### `Promise`

L'API Promise est un système qui vient se substituer au callback quand
il s'agit de gérer des appels asynchrones. Voyons à quoi ressemble le
code précédent avec des promesses :

```javascript
const request = require('request-promise-native');
const fs = require('fs').promises;

request.get('https://geographer.fr/')
    .then(r => fs.writeFile('/tmp/result_promise.txt', r))
    .then(r => fs.copyFile('/tmp/result_promise.txt', '/tmp/copy_promise.txt'))
    .then(() => console.log('Work is done!'))
    .catch(e => console.error(e));
```

Beaucoup mieux ! On remarque deux méthodes : `then` et `catch`, et
l'objet sur lequel elles sont appliquées n'apparait pas clairement. Il
s'agit en fait d'un objet `Promise` qui vient enrober les valeurs de
retour des appels asynchrones. Pour mieux comprendre, étudions ce code
qui implémente une fonction retournant une promesse :

```javascript
const fs = require('fs');

const writeFilePromise = (path, data) => new Promise((resolve, reject) => {
    fs.writeFile(path, data, (err, result) => {
        if (err) {
            reject(err);
            return;
        }

        resolve(result);
    });
});

writeFilePromise('/tmp/hello.txt', 'Hello!')
    .then(() => console.log('Work is done!'))
    .catch(e => console.error(e));
```

On obtient donc une fonction `writeFilePromise` qui se substitue à
`fs.writeFile`. Cette nouvelle fonction ne prend pas de callback en
paramètre mais retourne immédiatement une variable `Promise`. La
fonction à exécuter est passée en paramètre au constructeur `Promise`.
Cette fonction reçoit deux autres fonction en paramètre : `resolve`, et
`reject`. La première sera appelée lorsqu'il faut transférer une valeur
de retour qui n'est pas une erreur. La seconde sera appelée afin de
transférer une erreur.

Toujours au sein de la fonction anonyme passé en paramètre à `Promise`,
on retrouve finalement l'appel à `fs.writeFile`. Ce dernier prend
toujours un callback en paramètre mais maintenant que nous avons une
promesse à disposition, nous pouvons utiliser sa fonction de résolution
(`resolve`) et de rejet (`reject`) afin d'exfiltrer les valeurs de
retour afin de ne pas créer de *callback hell*.

Revenons au dernier bloc de code, l'appel à `writeFilePromise`. Nous
savons maintenant que cette fonction retourne un objet `Promise`. Cet
objet admet différentes méthodes, dont `then` et `catch`. La méthode
`then` est appelée lorsque c'est `resolve` qui a été appelé dans le
callack de promesse (donc, lorsqu'il n'y a pas eu d'erreur). La
méthode `catch` est appelée lorsque c'est `reject` qui a été appelé
dans le callback de promesse. Les méthodes `then` et `catch` admettent
des fonctions en paramètre. Ces fonctions reçoivent elles-mêmes en
paramètres les valeurs qui ont été passés à `resolve` et `reject`.

Enfin, on peut noter qu'il est possible d'enchainer les promesses,
comme on a pu le voir plus haut. On se retrouve alors avec une
construction très lisible qu'on appelle une chaine de promesse. De ce
fait découle la possibilité de ne placer qu'un seul `catch`, à la fin
de la chaine. Celui-ci couvre les erreurs de l'intégralité de la
chaine, ce qui allège considérablement le code (mais ammène d'autres
problèmes, malheureusement c'est hors-sujet).

### `Async`/`Await`

Les mots clés `async` et `await` sont des sucres syntaxiques autour des
promesses. Ils permettent d'écrire du code très lisible, plus proche du
schéma de pensée séquentielle auquel nous sommes généralement habitués.
Voyons tout de suite un exemple :

```javascript
const request = require('request-promise-native');
const fs = require('fs').promises;

const main = async () => {
    const body = await request.get('https://geographer.fr/');
    await fs.writeFile('/tmp/result_async.txt', body);
    await fs.copyFile('/tmp/result_async.txt', '/tmp/copy_async.txt');
    console.log('Work is done!');
};

main().catch(e => console.error(e));
```

La fonction `main` est marquée `async` : on pourra donc utiliser le mot
clé `await` dans son scope. On remarque ensuite que le mot clé `await`
semble automatiser la résolution de l'objet `Promise` qui est retourné
par les différents appels asynchrones. D'une part, le mot clé `await`
fait office de barrière : on ne passe pas à l'instruction suivante tant
que la promesse n'est pas résolue. D'autre part, il permet d'extraire
le résultat de l'objet `Promise` (ce que l'on recevait auparavant dans
le callback côté `then`) lors qu'il n'y a pas d'erreur.

Il semble il y avoir un problème avec ce code : le cas d'erreur n'est
pas gêré. C'est vrai : on aurait pu utiliser un `try`/`catch` afin de
récupérer une eventuelle erreur. Mais on peut aussi profiter d'une
autre propriété intéressante des promesses. Si une promesse n'est pas
gêrée dans son scope courant, elle est remontée au scope parent.
L'erreur sera donc gêrée au niveau du `main().catch()`. On comprend
alors qu'une fonction marquée `async` retourne une `Promise`.

### Un crawler concurrent

Pour conclure notre petite balade dans le monde féérique de la
concurrence, nous allons nous faire un petit crawler qui visite des
pages web et nous liste toutes celles contenant le mot \"JavaScript\".

```javascript
const request = require('request-promise-native');
const PAGES = [...]; // Truncated

const work = async page => {
    const url = `https://blog.geographer.fr/${page}`;
    const body = await request.get(url);
    return { result: body.toLowerCase().includes('javascript'), url };
}

console.log(`Crawling ${PAGES.length} pages...`);
const tasks = PAGES.map(work);

Promise.all(tasks)
    .then(r => r.filter(e => e.result).forEach(e => console.log(e.url)))
    .catch(console.error);
```

On remarque la méthode statique `Promise.all` qui prend un tableau de
`Promise` et nous renvoie un tableau de résultats.

Voici un équivalent Python :

```python
import requests

PAGES = []  # Truncated

results = []
for page in PAGES:
    url = f'https://blog.geographer.fr/{page}'
    response = None

    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    results.append({
        'result': 'javascript' in response.text.lower(),
        'url': url
    })

for e in list(filter(lambda r: r['result'], results)):
    print(e['url'])
```

Bien entendu, il est absurde de comparer une implémentation concurrente
JavaScript avec une implémentation non-concurrente Python. Nous allons
donc les comparer:

```
$ time node crawler.js > /dev/null
Executed in  712,13 millis    fish           external
   usr time  295,40 millis  111,00 micros  295,29 millis
   sys time   74,41 millis  557,00 micros   73,85 millis

$ time python crawler.py > /dev/null
Executed in    1,48 secs   fish           external
   usr time  651,95 millis   92,00 micros  651,86 millis
   sys time   61,17 millis  487,00 micros   60,68 millis
```

La version écrite en JavaScript est environ deux fois plus rapide. Le
nombre de lignes écrites est très similaire.
