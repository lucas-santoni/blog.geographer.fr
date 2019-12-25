---
title: "[FRENCH] Introduction à z3, solveur de crackmes"
slug: z3-intro
date: 13/07/2017
---

z3 est un **démonstrateur automatique de théorème** (*theorem prover* en
anglais, mais la traduction est vachement plus drôle...). C'est un logiciel
auquel on dit "j'ai 5 équations que voici et 10 inconnues que voilà, trouve une
solution". Alors z3 travaille dans son coin et quelques secondes (ou parfois
années) plus tard, il ressort avec **un système solution** de l'équation.

## Un monde de contraintes

Ces équations, ce sont **des contraintes**. On peut exprimer beaucoup de choses
avec des **opérateurs mathématiques** et les **structures de controle** d'un
langage. Avec z3, il est facile de traduire des contraintes du genre "trouve
moi une suite de 5 nombres entiers commençant à 13 et membres de la table de 7,
chacun étant au moins le double du précédent mais jamais plus de son triple, la
somme de ces 5 nombres donnant un résultat multiple de 44". Si il existe bien
une suite de 5 nombres qui vérifient toutes ces contraintes, z3 les trouvera.
On dit alors que z3 fournit **un modèle**.

```
➜  ~ python article.py
13
28
56
112
231

Numbers: 5
Sum: 440
44 modulus: 0
➜  ~
```

Certes, cet exemple est un peu inutile mais pas si éloigné de ce qu'on fait
lorqu'on résout des crackmes avec z3. Le code est [disponible
ici](/assets/z3/z3_demo.py).

![constraints](/assets/z3/constraints_everywhere.jpg)

[z3 est un projet de Microsoft](https://github.com/Z3Prover/z3). Le coeur est
développé en C++ et des **bindings** pour plusieurs langages sont disponibles.
On se concentrera ici sur le **binding Python** qui est le plus répandu.

z3 est un outil pour les mathématiciens comme en attestent [ces
documents](https://github.com/Z3Prover/z3/wiki/Publications) emplis de magie
noire. Mais c'est aussi un super outil pour résoudre **vite** des épreuves ou
même plus généralement des problèmes de reverse.

## Le solveur de crackmes

Schéma classique... On est en CTF, épreuve de reverse à 200 points. C'est un
code Javascript obfusqué. Cool, ça change des routines en assembleur et des F5
dans IDA. On étudie le code, on nettoie le tout et on valide que ça
fonctionne dans l'interpréteur Node. Ok, on a un code nettoyé qui ressemble à
ça :

``` javascript
const check = (valid) => {
  // Array used for algo
  const tab = 'azertyuiopqsdfghjklmwxcvbnAZERTYUIOPQSDFGHJKLMWXCVBN0123456789_$&#@';
  const checksum = valid; // Valid checksum

  const input = process.argv[2]; // User input
  if (!input)
    return console.log('[NO INPUT] KO.');
  const len = input.length; // Length has to ben 10
  if (len != 10)
    return console.log('[BAD LENGTH] KO.');
  let sum = 1337; // Initial sum

  // Routinz
  for (let i = 0; i < len; i++) {
    // Get values from tab
    // Values between 0 and 66 both included
    let index = tab.indexOf(input.substring(i, i + 1));

    // Mathematics omg
    sum = sum + 42 + ((index * len * (i + 1)) * 13);
  }

  // Final check
  if (sum == checksum)
    // Goodboy
    return console.log('[' + input + ']' + '[' + sum + ']' + ' OK.');
  // Badboy
  console.log('[' + input + ']' + '[' + sum + ']' + ' KO.');
};

// Entry point
check(332867);
```

_**Note** : ce code est issu d'une épreuve de [Newbie
Contest](https://www.newbiecontest.org). Il a été modifié afin de ne pas spoil
l'épreuve._

Et là c'est le drame... Y'a une **routine de calcul** à comprendre mais il est
tard, on a **la flemme** et en plus on a trop picolé. Bon, commençons par résumer
ce que l'on sait :

  * Un flag fait 10 caractères
  * A chaque caractère du flag correspond un nombre entre 0 et 66
      tous deux inclus
  * Un flag valide vérifie une routine de calcul connue
  * La somme calculée doit être égale à 332867
  * Il y a surement beaucoup de flags valides mais un seul suffit

Et plusieurs solutions permettent de **résoudre ce problème** :

  * Faire de la magie noire sur papier et sortir un flag de nul part en
      résolvant les équations à la main
  * Générer un dictionnaire de flags et tenter de les valider en exploitant la
      routine connue (bruteforce de gros porc en fait)
  * Faire du z3

## Faire du z3 (avec Python)

Pour faire du z3 avec Python, **il faut** :

  * Installer le binding
  * Définir les inconnues
  * Définir les contraintes
  * D'autres trucs parfois, mais ça c'est la base

Commençons par installer z3. Il existe des bindings pour Python 2 et 3 et on
peut tous deux les installer avec pip. Nous allons faire du Python 2, donc :

```
➜  ~ pip install z3-solver
➜  ~
```

Attention au nom du paquet ! `z3` est également un nom de paquet valide mais il
installe totalement autre chose.

On va commencer par **poser quelques variables** :

``` python
# Import z3
from z3 import IntVector, Solver, unsat

# Serial length
n = 10

# Variables used by z3
flag = IntVector('f', n)
sums = IntVector('s', n)

# Tab to get chars
tab = ('azertyuiopqsdfghjklmwxcvbn'
       'AZERTYUIOPQSDFGHJKLMWXCVBN0123456789_$&#@')

# Final flag
final = ''

# Main z3 object
s = Solver()
```

On a récupéré la longeur du flag ainsi que `tab` dans le code original. Le type
`intVector` est apporté par z3, c'est simplement **un genre de liste** de `n`
nombres entiers que le framework peut manipuler. `flag` représente donc les 10
nombres inconnus qui donneront des caractères. `sums` représente les 10 sommes
associés.

En effet, **chaque nombre à trouver est relié au précédent via une somme**. On
sait également que chaque nombre a une valeur **entre 0 et 66** et que la somme
finale est **332867** tandis que celle de départ est **1337**. On balance tout
ça bêtement dans z3 à l'aide de la méthode `add()` de notre objet `s` :

``` python
# Iterate on serial length
# Values between 0 and 66 both included
# If first iteration, sum is at 1337
# Otherwise use previous sum
for i in range(n):
    s.add(flag[i] >= 0)
    s.add(flag[i] <= 66)
    if i != 0:
        s.add(sums[i] == sums[i - 1] + 42 + ((flag[i] * n * (i + 1)) * 13))
    else:
        s.add(sums[i] == 1337 + 42 + ((flag[i] * n * (i + 1)) * 13))

# Final sum to get
s.add(sums[n - 1] == 332867)
```

Ce petit bout de code illustre bien toute la puissance de z3 : **il n'y a
aucune différence entre le code source que l'on est en train d'écrire et les
données (inconnues, contraintes...) que l'on manipule**. Le tout se confond et
cela permet d'utilier la flexibilité de Python dans la rédaction même de nos
contraintes.

Enfin, on laisse z3 travailler :

``` python
# Let z3 do the work
if s.check() != unsat:
    m = s.model()

    # Get clean flag
    for f in flag:
        final += tab[m[f].as_long()]
    print final
else:
    print "No solution found."
```

La méthode `s.check()` sert à vérifier si z3 peut trouver au moins un modèle
vérifiant les contraintes posées (`unsat`, pour *unsatisfied* est une valeur
apportée par z3). Si c'est le cas, on peut appeler la méthode `s.model()` qui
renvoie ce modèle. Le modèle est encore une fois un genre de liste. Chaque
élément de la liste n'est pas une valeur mais **un objet qui peut être manipulé
par z3**. On utilise alors des méthodes tels que `m[f].as_long()` pour effecter
une conversion en valeur brute.  On remarque alors que **les index utilisés**
pour parcourir le modèle sont en fait **les inconnues** que
nous avons posées.

On exécute et...

```
➜  ~ python solve.py
Gaz&j@a@@#
➜  ~ node challenge.js "Gaz&j@a@@#"
[Gaz&j@a@@#][332867] OK.
➜  ~
```

Ah ben trop fort ! On va générer quelques solutions supplémentaires pour
le fun :

``` python
# Let z3 do the work
while s.check() != unsat:
    m = s.model()

    # Get clean flag
    for f in flag:
        final += tab[m[f].as_long()]
        s.add(Or(f != m[f]))

    print final
    final = ''
else:
    print "No solution found."
```

A chaque fois qu'un modèle est trouvé, on rajoute une contrainte
supplémentaire : tous les caractères du prochain flag devront être différents
des précédents.  Il est bien sur possible de générer encore plus de flags avec
des contraintes moins restrictives du type `s.add(Or(flag[0] != m[flag[0]]))`
(seul le premier caractère doit être différent).

```
➜  ~ python solve.py
Gaz&j@a@@#
araaz$@8&&
zeeqa_#7$$
ez#ph97P__
y5&og86O29
74$if75I18
Ht8Nd64U07
FY7Bs53YN6
DT6Li42TB@
S9@Vq31RV5
Q85Mp20Z74
P74Ko1NE#1
@&_Ju0BA93
&_9GtB&x82
$@UHy&$n60
_#1Fr#8b5N
#$OmeN_14B
9BIwkV903V
8VYh5CVNCC
MMTg$XC3XX
LLRd_WX#ML
JKEf9MW&WW
KJVs8LM$LM
1C3u@KL_KK
3X2l#JK9JJ
2WC_&QJBHH
5EX@4HH5GG
4FW#6GG6FF
660$7FD4DD
No solution found.
➜  ~
```

Le code complet est [disponible ici](/assets/z3/z3_js_challenge.py).

## Le mot d'la fin

z3 est donc un logiciel puissant qui se prête très bien à la résolution de
crackmes. La phase de reverse en elle même ne change pas vraiment, il faut
toujours avoir une bonne compréhension de la routine utilisée par le crackme
afin de la poser dans z3. En revanche, la rédaction d'un keygen est beaucoup
plus facile et on élimine tout bruteforce. On peut aussi utiliser z3 en
intéractif pour résoudre rapidement de petits problèmes dans la résolution
d'une épreuve.

z3 est un projet qui commence à être bien à la mode dans le milieu de la
sécurité et il est activement développé, à suivre...
