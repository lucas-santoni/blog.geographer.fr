from z3 import IntVector, Solver, unsat

vectorLen = 5
modulus = 44
numbers = IntVector('n', vectorLen)

s = Solver()

s.add(numbers[0] == 13)
total = numbers[0]
for i in range(1, vectorLen):
    s.add(numbers[i] >= numbers[i - 1] * 2)
    s.add(numbers[i] <= numbers[i - 1] * 3)
    s.add(numbers[i] % 7 == 0)
    total += numbers[i]

s.add(total % modulus == 0)

if s.check() != unsat:
    m = s.model()
    final = 0
    for n in numbers:
        final += m[n].as_long()
        print m[n].as_long()

    print "\nNumbers: %d" % len(numbers)
    print "Sum: %d" % final
    print "%d modulus: %d" % (modulus, final % modulus)
else:
    print "No model found..."
