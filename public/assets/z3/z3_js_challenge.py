# Import z3
from z3 import IntVector, Solver, unsat, Or

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
