---
title: Hexpresso FIC Quals 2019: Step 3
slug: hexpresso-fic-3
date: 19/12/2019
---

The third step is a forensics challenge.

![Introduction](/assets/hexpresso-fic-quals/step3/intro.png)

We are given a `.raw` file that is apparently the dump of a USB stick:

```
$ file 76b0c868ab7397cc6a0c0a1e107e3079.raw
76b0c868ab7397cc6a0c0a1e107e3079.raw: DOS/MBR boot sector MS-MBR Windows 7 english at offset 0x163 "Invalid partition table" at offset 0x17b "Error loading operating system" at offset 0x19a "Missing operating system", disk signature 0x47e6da9e; partition 1 : ID=0x7, start-CHS (0x0,2,3), end-CHS (0xc5,3,19), startsector 128, 198656 sectors
```

Standard recovery tools like
[PhotoRec](https://www.cgsecurity.org/wiki/PhotoRec_FR) seem to *understand*
the dump but can not actually recover any file.

After taking a look at writeups of similar challenges, we decided to try a
[BitLocker](https://fr.wikipedia.org/wiki/BitLocker_Drive_Encryption)
bruteforce. The combination of
[Dislocker](https://wreckedsecurity.com/encryption-and-data-protection/brute-force-dictionary-attack-against-bitlocker/)
and `rockyou.txt` reveals the password: `password`.

Dislocker also allows to mount the volume and retrieve its files. Let's open
`flag.txt`:

```
# cat flag.txt
Every Forensic investigation starts with a good bitlocker inspection.
-- @chaignc

Try Harder !
```

Well... We also have another file, that we'll call `volume.img`:

```
$ file volume.img
volume.img: DOS/MBR boot sector, code offset 0x52+2, OEM-ID "NTFS    ", sectors/cluster 8, Media descriptor 0xf8, sectors/track 63, heads 16, hidden sectors 128, dos < 4.0 BootSector (0x80), FAT (1Y bit by descriptor); NTFS, sectors/track 63, sectors 198655, $MFT start cluster 8277, $MFTMirror start cluster 2, bytes/RecordSegment 2^(-1*246), clusters/index block 1, serial number 08618333c18332a97; contains bootstrap BOOTMGR
```

No time to mount the volume properly, let's use `binwalk` and extract the ZIP
file it contains:

```
$ binwalk volume.img

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
33969512      0x2065568       Zip archive data, at least v2.0 to extract, compressed size: 66, uncompressed size: 68, name: fic.txt
33969720      0x2065638       End of Zip archive, footer length: 22
33970536      0x2065968       Zip archive data, at least v2.0 to extract, compressed size: 66, uncompressed size: 68, name: fic.txt
33970744      0x2065A38       End of Zip archive, footer length: 22
33971560      0x2065D68       Zip archive data, at least v2.0 to extract, compressed size: 66, uncompressed size: 68, name: fic.txt
33971768      0x2065E38       End of Zip archive, footer length: 22
33972584      0x2066168       Zip archive data, at least v2.0 to extract, compressed size: 66, uncompressed size: 68, name: fic.txt
33972792      0x2066238       End of Zip archive, footer length: 22
33973608      0x2066568       Zip archive data, at least v2.0 to extract, compressed size: 66, uncompressed size: 68, name: fic.txt
33973816      0x2066638       End of Zip archive, footer length: 22
57040896      0x3666000       ELF, 64-bit LSB shared object, AMD x86-64, version 1 (SYSV)
57137325      0x367D8AD       Copyright string: "Copyright (C) 1996-2018 Free Software Foundation, Inc."
57137480      0x367D948       Copyright string: "copyright notice and this notice are preserved."
57141772      0x367EA0C       Unix path: /usr/share/locale
57154816      0x3681D00       Copyright string: "Copyright %s %d Free Software Foundation, Inc."
```

There is a link to a GitHub Gist inside the extracted archive:

```
$ cat fic.txt
https://gist.github.com/bosal43833/3e815abc3f92e45963a8aafc8acfe411
```

Which contains our flag in base64:

![GitHub Gist](/assets/hexpresso-fic-quals/step3/gist.png)

Final flag:

```
$ echo -n "aHR0cHM6Ly9jdGYuaGV4cHJlc3NvLmZyLzFlYTk2N2Y1MmQxYWFiMzI3ZDA4NGVmZDI0ZDA0OTU3Cg==" | base64 -D
https://ctf.hexpresso.fr/1ea967f52d1aab327d084efd24d04957
```

[Click here](/posts/hexpresso-fic-4) for the next step!