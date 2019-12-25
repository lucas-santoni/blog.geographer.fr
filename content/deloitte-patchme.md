---
title: Deloitte CTF Quals 2019: PatchMe 🤕
slug: deloitte-patchme
date: 06/11/2019 01
---

*PatchMe* 🤕 was a task labelled reversing and worth 150 points. It is a PE
crackme.

![Task Description](/assets/patchme/intro.png)

We are given a binary that checks whether we are registered or not. There is
no serial to input or anything so we can assume that the protection relies on
some environmental observations.

![Not Registered](/assets/patchme/not_registered.png)

Let's load it into IDA and take a look at the imports...

![IDA Imports](/assets/patchme/ida_imports.png)

We can see various functions that allows to interact with the system:
`RegOpenKeyExA`, `GetSystemTime`, `ReadFile`... We also have
`IsDebuggerPresent` that we should keep in mind if we decide to do some
debugging.

What about the strings?

![IDA Strings](/assets/patchme/ida_strings.png)

*And the flag is...* looks very promising. If we cross reference, we end up
here:

![IDA Routinz](/assets/patchme/ida_routinz.png)

This is the top level of the verification routine (offset `0040102B`). We can
clearly see that we should take the first two jumps, and not take the next
two ones.

Then, we have a bunch of calls. The flag is displayed using a message box
after that. Let's take a look at one of these calls:

![IDA Call](/assets/patchme/ida_call.png)

The function does not look very coherent and IDA is not even able to analyse
it correctly. If we look at the block on the left, we notice that it performs
a xor operation using the bytes that actually correspond to the code of the
block on the right (highlighted in yellow). So the function decrypts itself
at runtime. All the eight calls follow the same structure. I guess it's time
to move to the debugger.

Using x64dbg, we will set a breakpoint on `0040102B` (offset of the routine).
Then we start to trace, updating the Z flag in order to take the right paths.

![Debugger Go](/assets/patchme/dbg_go.png)

We then reach the first call. We will let the function decrypt itself so that
we can analyse it.

![Debugger Decrypt](/assets/patchme/dbg_decrypt.gif)

All the decrypted calls follow the same logic. Some external operation (for
example, checking if a file exists) is performed. If it fails, a fake and
incorrect key is used to update some piece of global memory (which ultimaletly
becomes the flag). However, if it succeeds, the piece of memory is updated
correctly.

The operations are as follows:

* Call 1 -> Read a file
* Call 2 -> `IsDebuggerPresent`
* Call 3 -> Read a registry key
* Call 4 -> Computer name has to be `DCTF_2019`
* Call 5 -> Username has to be `#DELo1tteP1ayer`
* Call 6 -> Compare system time to some value
* Call 7 -> Compare system time to some value again
* Call 8 -> `IsDebuggerPresent` again

In order to solve the challenge, I traced into each call, manually updating
the Z flag when necessary so that the binary would think that all the
operations succeeded, when none of them actually did.

Once we passed the calls, the `Strstr` function is used to check if the
global memory chunk contains `CTF{`, which should be the case if all the calls
went smooth.

We can then resume execution and:

![Final flag](/assets/patchme/final.png)

The final flag is: `DCTF{Th353_ch3ck5_4r3_XOR-bit-ant}`.