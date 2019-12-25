---
title: Santhacklaus 2019: NSAR
slug: santa-nsar
date: 23/12/2019
---

**Before we start!** This post is authored by [@pwnh4](https://twitter.com/pwnh4).
I'm really proud to have him for this guest post as he started computer security
only a few months ago with my [2019 Piscine](https://blog.geographer.fr/posts/piscine-poc-2019)
but already performs very well in CTF. Go follow him!

***

*NSAR* is a reverse/crypto/stegano 600 points challenge of the Santhacklaus
2019 CTF.

![NSAR](/assets/santa/nsar/chall.png)

## First contact

The description of the challenge lets us know that the goal is to reverse
engineer a custom file format (NSAR) used to compress and encrypt multiple
files. We download the two files :

### nsar

It is the program used to compress and encrypt multiple files to a `.nsar`
archive. We can use it pretty easily:

```
➜  ./nsar         
Enter path to files (max 255 files):
> ./toast.pdf
> ./blackhole.gif
> 
2 files selected.
Key for encryption (empty = no encryption): MYKEY42
Encryption
Output: out.nsar

➜  hexdump -C out.nsar | head  
00000000  4e 53 41 52 00 01 01 02  00 00 00 00 00 00 00 00  |NSAR............|
00000010  62 6c 61 63 6b 68 6f 6c  65 2e 67 69 66 00 30 00  |blackhole.gif.0.|
00000020  00 00 74 6f 61 73 74 2e  70 64 66 00 96 76 69 00  |..toast.pdf..vi.|
00000030  1f 8b 08 00 00 00 00 00  00 03 00 1b 40 e4 bf 0a  |............@...|
00000040  10 0d 7d 60 55 22 49 01  49 98 00 00 00 00 00 40  |..}`U"I.I......@|
00000050  00 00 22 33 00 7b 4a 00  77 36 00 74 5b 00 06 5a  |.."3.{J.w6.t[..Z|
00000060  00 7f 48 00 1c 43 00 54  35 00 31 42 00 28 3e 00  |..H..C.T5.1B.(>.|
00000070  34 55 00 c4 54 00 ba 42  00 c4 55 00 a2 20 00 c4  |4U..T..B..U.. ..|
00000080  58 00 fa 20 00 e4 4c 00  f4 4e 35 89 55 58 8d 5e  |X.. ..L..N5.UX.^|
00000090  5b 80 13 49 95 6f 47 66  12 28 8f 71 48 29 73 21  |[..I.oGf.(.qH)s!|
```

### archive.nsar

An NSAR archive created with the above program by the creator of the
challenge. We can see that a lot of files in various formats have been put in
this archive. One of them surely contains the flag!

```
➜  hexdump -C archive.nsar | head -n 20
00000000  4e 53 41 52 00 01 01 1c  00 00 00 00 00 00 00 00  |NSAR............|
00000010  61 2e 6f 75 74 00 7f 01  00 00 62 62 62 2e 6d 70  |a.out.....bbb.mp|
00000020  34 00 2b 3e 00 00 63 64  2e 67 69 66 00 79 98 0f  |4.+>..cd.gif.y..|
00000030  00 64 6c 70 6d 6a 63 63  2e 77 6d 76 00 52 76 30  |.dlpmjcc.wmv.Rv0|
00000040  00 65 2e 67 69 66 00 71  fe 63 00 66 6c 61 67 2e  |.e.gif.q.c.flag.|
00000050  6f 64 74 00 01 b7 64 00  66 72 2e 67 69 66 00 00  |odt...d.fr.gif..|
00000060  30 65 00 68 2e 67 69 66  00 6a 6d 6b 00 68 64 75  |0e.h.gif.jmk.hdu|
00000070  2e 70 6e 67 00 a2 09 6d  00 6a 2e 67 69 66 00 56  |.png...m.j.gif.V|
00000080  54 6f 00 6d 61 72 69 6f  2e 67 69 66 00 ed 03 70  |To.mario.gif...p|
00000090  00 6e 6f 74 68 69 6e 67  2e 70 6e 67 00 7e 28 72  |.nothing.png.~(r|
000000a0  00 6f 6b 2e 6d 70 33 00  69 2f 72 00 6f 6b 62 72  |.ok.mp3.i/r.okbr|
000000b0  6f 2e 70 6e 67 00 e1 bf  75 00 70 61 70 61 6e 6f  |o.png...u.papano|
000000c0  65 6c 2e 70 6e 67 00 ed  78 76 00 72 65 61 6c 5f  |el.png..xv.real_|
000000d0  73 61 6e 74 61 2e 70 6e  67 00 5f cd 7b 00 73 2e  |santa.png._.{.s.|
000000e0  67 69 66 00 26 10 7f 00  73 61 64 2e 67 69 66 00  |gif.&...sad.gif.|
000000f0  5a ab 80 00 73 61 6e 74  61 2e 62 6d 70 00 71 fd  |Z...santa.bmp.q.|
00000100  e3 00 73 61 6e 74 61 2e  67 69 66 00 a7 bc fa 00  |..santa.gif.....|
00000110  73 61 6e 74 61 66 6c 61  67 2e 70 64 66 00 80 28  |santaflag.pdf..(|
00000120  12 01 73 61 6e 74 61 7a  69 63 2e 6d 70 33 00 f0  |..santazic.mp3..|
00000130  60 17 01 73 65 63 72 65  74 2e 6a 70 67 00 07 a4  |`..secret.jpg...|
```

## Reversing the NSAR file format

To extract the files stored in the NSAR archive, we need to understand how
this file format works. To do so, we start reversing the NSAR program. First
let's have an overview of the binary :

```
➜  file nsar 
nsar: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=efd6544321a3657b6e164861d1b1cb319c1ad3d6, for GNU/Linux 3.2.0, not stripped

➜  rabin2 -I nsar
arch     x86
baddr    0x0
binsz    61416
bintype  elf
bits     64
canary   false
class    ELF64
compiler GCC: (Debian 9.2.1-19) 9.2.1 20191109
crypto   false
endian   little
havecode true
intrp    /lib64/ld-linux-x86-64.so.2
laddr    0x0
lang     c++
...
```

It's an ELF 64 bits binary coded in C++ for the x86 architecture. It's now
time to launch IDA.

The main function of the program consists of the multiple input prompts we
saw earlier. The most important line is the one that comes near the end:

```cpp
create_nsar((__int64)&OUTPUT_FILENAME, (__int64)&ENCRYPTION_KEY, (__int64)&FILEPATHES_TO_COMPRESS);
```

`create_nsar` starts by defining two double-ended queues, which are basically
queues with two edges: you can get, push or pop stuff both at the front and
at the end of these queues.

```cpp
std::deque<std::fpos<__mbstate_t>,std::allocator<std::fpos<__mbstate_t>>>::deque(&QUEUE_DOUBLE_E_1);
std::deque<std::fpos<__mbstate_t>,std::allocator<std::fpos<__mbstate_t>>>::deque(&QUEUE_DOUBLE_E_2);
```

We can divide the rest of the function in three main parts...

## Creation of the nsar header

```cpp
v29 = 78; // 'N'
v30 = 83; // 'S'
v31 = 65; // 'A'
v32 = 82; // 'R'

// non relevant code ellapsed

std::basic_ofstream<char,std::char_traits<char>>::basic_ofstream((__int64)&OSSTREAM, OUTPUT_FILENAME, v3);
std::ostream::write((std::ostream *)&OSSTREAM, &v29, 16LL);
```

Those few lines show us the beginning of the NSAR header : the bytes `NSAR`
are written, followed by 12 NULL bytes (because the write() is done on 16
bytes). Note that here, `OSSTREAM` refers to the output file stream.

Then the program iterates over all input files :

```cpp
while ( (unsigned __int8)std::operator!=(&beginning, &end) )
{
  // 1
  first_element = std::_Rb_tree_const_iterator<std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>>::operator*(&beginning);
  extract_filename_from_path(&FILENAME, first_element);
  string = (char *)std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::c_str(&FILENAME);
  len = std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::length(&FILENAME);    
  
  // 2
  std::ostream::write((std::ostream *)&OSSTREAM, string, len + 1);

  // 3
  position = std::ostream::tellp((std::ostream *)&OSSTREAM);
  std::deque<std::fpos<__mbstate_t>,std::allocator<std::fpos<__mbstate_t>>>::push_back(&QUEUE_DOUBLE_E_1, &position);

  // 4
  number_wtf = 1061109567;
  std::ostream::write((std::ostream *)&OSSTREAM, (const char *)&number_wtf, 4LL);

  v41 = v5;
  std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::~basic_string(&FILENAME);
  std::_Rb_tree_const_iterator<std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>>::operator++(&beginning);
}
```

For each file:

1. Get the filename
2. Write this name in the output file + 1 NULL byte (`len + 1`)
3. Save the current position in the output buffer in the first deque `QUEUE_DOUBLE_E_1` 
4. Write an integer (4 bytes) to the output file

We can know start to tell the format of the header:

```
NSAR + 0x0 * 12 + filename1 + 0x0 + 4bytesInteger + filename2 + 0x0 + 4bytesInteger + ... 
```

After this loop, the output file stream is closed. We are now going to see how the body of the file is defined.

## Creation of the nsar body

The output file is then re-opened with `gzopen`, this tells us that in the
rest of the function, we will interact with the output file as a GZ
compressed file.

In this part, the program iterates once again over the input files:

```cpp
while ( (unsigned __int8)std::operator!=(&beginning2, &end2) )
{
  // 1
  first_element_2 = std::_Rb_tree_const_iterator<std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>>::operator*(&beginning2);
  std::basic_ifstream<char,std::char_traits<char>>::basic_ifstream(&FILENAME, first_element_2, 4LL);// set current FILENAME
  
  // 2
  std::fpos<__mbstate_t>::fpos(&pos_actuelle, long_position);
  std::deque<std::fpos<__mbstate_t>,std::allocator<std::fpos<__mbstate_t>>>::push_back(
    &QUEUE_DOUBLE_E_2,
    &pos_actuelle);
  if ( (unsigned __int8)std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::empty(ENCRYPTION_KEY) != 1 )
  {

    // 3
    file_content = std::basic_ifstream<char,std::char_traits<char>>::rdbuf(&FILENAME);
    key = std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::c_str(ENCRYPTION_KEY);
    key_length = std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::length(ENCRYPTION_KEY);
    do
    {
      charr = std::basic_streambuf<char,std::char_traits<char>>::sgetc(file_content);
      x = 0;
      if ( charr )
      {
        x = charr ^ *(_BYTE *)(index % key_length + key);// <=> charr ^ key[index % len(key)]
        if ( !x )
          x = charr;
      }
      else
      {
        x = 0;
      }

      // 4
      nb_written_should_be_one = gzwrite(gzFile, &x, 1LL);
      long_position += nb_written_should_be_one;
      ++index;
    }
    while ( (unsigned int)std::basic_streambuf<char,std::char_traits<char>>::snextc(file_content) != -1 ); // while we're not at the end of the input file
  }
}
```

Some explanations:

1. Open the current file
2. Push current position in output file to the **second** deque
3. Here is the code defining the encryption process of the input file. It is a repeated XOR encryption, with a few exceptions:
    1. If the byte of the input file we currently want to XOR is null, we do not XOR it
    2. If the result of the XOR is null, we do not XOR the current byte of the input file
4. Write the encrypted byte with `gzwrite`

*What does `gzwrite` do ?*

At first I thought that it wouldn't compress anything because we use
`gzwrite` to write one byte at the time. To check if my assumption was
correct, I created a new NSAR archive containing only a `toast.pdf` file.
Thanks to what we've learnt so far, we can tell the length of the
corresponding archive header : `len("NSAR") + 12 + len("toast.pdf") + 1 + 4 = 30`

```
➜  tail -c +31 out.nsar | hexdump -C | head
00000000  1f 8b 08 00 00 00 00 00  00 03 8c ba 63 90 2e 3c  |............c..<|
00000010  d0 36 38 33 67 6c db e6  3d b6 6d db b6 6d db 3a  |.683gl..=.m..m.:|
00000020  63 db b6 6d 7b ce d8 b6  3d fb bc fb bd 5b 5b b5  |c..m{...=....[[.|
```

We can see that the body of the NSAR file starts with `1f 8b 08` which are
the first bytes of the gzip file format.

So it appear that `gzwrite` is using a buffer to store all the written
input and wait for `gzclose` to compress it and write it to the output
file.

## Final header

At the end of the function, we see this loop which iterates over all input filenames:

```cpp
while ( (unsigned __int8)std::operator!=(&beg, &endd) )
{   
  // 1
  front_header = (__int64 *)std::deque<std::fpos<__mbstate_t>,std::allocator<std::fpos<__mbstate_t>>>::front(&QUEUE_DOUBLE_E_1);
  std::ostream::seekp((__int64)&OSSTREAM, *front_header, front_header[1]);
  std::deque<std::fpos<__mbstate_t>,std::allocator<std::fpos<__mbstate_t>>>::pop_front(&QUEUE_DOUBLE_E_1);
  
  // 2
  v13 = (const char *)std::deque<std::fpos<__mbstate_t>,std::allocator<std::fpos<__mbstate_t>>>::front(&QUEUE_DOUBLE_E_2);
  std::ostream::write((std::ostream *)&OSSTREAM, v13, 4LL);
  std::deque<std::fpos<__mbstate_t>,std::allocator<std::fpos<__mbstate_t>>>::pop_front(&QUEUE_DOUBLE_E_2);
  
  std::_Rb_tree_const_iterator<std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>>::operator++(&beg);
}
```

1. take the first value of the FIRST deque (which points to the four byte
integer after a filename in NSAR header), go to it in the output file and pop
the value from the deque.
2. take the first value of the SECOND deque (which points to the beginning of
the corresponding file content before compression) and stores it in the
current position in the output buffer.

And tada! We now know how the NSAR file format works:

```
NSAR FILE FORMAT

*=======================HEADER PART=======================*

NSAR + 0x0 * 12 + filename1 + 0 + offset1 + filename2 + 0
 + offset2 + filename3 + 0 + offset3 + ...

*=======================BODY PART=========================*

---------------------GZIP COMPRESSED----------------------

contentOfFile1 + contentOfFile2 + contentOfFile3 + ...

----------------------------------------------------------

*=========================================================*
```

Where `offset{n}` is the position of the content of the nth file content in
the **uncompressed** body.

## Creating un-NSAR script

Now let's make a Python script that properly extracts and unciphers the files contained in the archive.

### Reading NSAR header

We retrieve the list of the files in the archive with their offset:

```python
def get_fileinfos(content: bytes) -> Tuple[str, int]:
    """
	reads the first filename and corresponding offset found in content
    """
    index = 0
    filename = ""
    while content[index] != 0:
        filename += chr(content[index])
        index += 1
    index += 1
    tmp = []
    for _ in range(4):
        tmp.append(content[index])
        index += 1
    offset = int(tmp[3] << 24 | tmp[2] << 16 | tmp[1] << 8 | tmp[0])  # little endian <3
    return filename, offset
```

We can now open the file and read all header :

```python
with open("/tmp/archive.nsar", "rb") as f:
    content = f.read()
c = content[16:]  # skip FORMAT name (NSAR) and padding
files = {}
ex_filename = None
while True:
    filename, offset = get_fileinfos(c)
    if offset == 0:  # end of header
        break
    files[filename] = {"offset": offset}
    if ex_filename:
       files[ex_filename]["length"] = files[filename].get("offset") - file[ex_filename].get("offset")
    ex_filename = filename
    c = c[len(filename) + 5:] # go to next file in header
```

We now have a dictionary `files` containing all archived files, their offset
and their length in uncompressed body.

### Uncompress the body

To retrieve the file, we need to uncompress the gzip-compressed body. This
can be done easily with the gzip module:

```python
import gzip

with open("/tmp/tmp.txt", "wb") as f:
    f.write(c)  # write only the compressed body
with gzip.open("/tmp/tmp.txt", "rb") as f:
    c = f.read()  # c now contains the uncompressed body
header_size = len(content) - len(c)
content = content[:header_size] + c
```

### Getting the key

We know that the body is XORed repetively with a key given by the chall
creator. And we also know that if `a ^ b = c`, then `a ^ c = b`

Thanks to that property, we will be able to retrieve the key because we know
a part of the plaintext that has been encrypted: the first bytes of the
header of the png format for example.

To get the key, we will XOR the first bytes of the encrypted png files with
the first bytes of png header. We will then be able to retrieve parts of the
keys (as it is a repetitive xor) and finally get the complete key.

Here is a function to check the part of key used at the beginning of an
encrypted png:

```python
def guess_png_key(files: dict, content: bytes, filename: str) -> None:
    offset = files[filename].get("offset")
    print(f"\n[*] trying to guess key at offset {offset} with {filename}")
    header = b"\x89PNG\x0d\x0a\x1a\x0a\x00\x00\x00\x0dIHDR\x00\x00\x00"  # mostcommon first fixed bytes in png headers
    guessed_key = ""
    for nb in range(len(header)):
        x = content[offset + nb] ^ header[nb]
        # don't forget the conditions we saw in the cpp code :
        if x == 0:  
            guessed_key += chr(content[offset + nb])
        else:
            guessed_key += chr(x)
    print(f"Possible part of key {guessed_key}")

guess_png_key(files, content, "okbro.png")
guess_png_key(files, content, "papanoel.png")
guess_png_key(files, content, "hdu.png")
guess_png_key(files, content, "yu.png")
guess_png_key(files, content, "nothing.png")
```

Which outputs:

```
[*] trying to guess key at offset 7716833 with okbro.png
Possible part of key Up3R_Sec_KEYT

[*] trying to guess key at offset 7764205 with papanoel.png
Possible part of key YTh1s_iS_sUp3P

[*] trying to guess key at offset 7145890 with hdu.png
Possible part of key sUp3R_Se7_KEY0

[*] trying to guess key at offset 23107299 with yu.png
Possible part of key cr37_KEYs_iS_^

[*] trying to guess key at offset 7481470 with nothing.png
Possible part of key My_sUp3Rcr37_X
```

We can know assemble the complete key used for encryption: `Th1s_iS_My_sUp3R_Secr37_KEY`.

### Extract files

Now, all we need is to uncipher the body and cut it in different files to retrieve the original input files:

```python
import os

def decrypt_all(files: dict, content: bytes, key: str) -> None:
    directory = f"_extracted_{sys.argv[1]}"
    os.mkdir(directory)
    j = 0
    for file in files:
        with open(f"{directory}/{file}", "wb") as f:
            offset = files[file].get("offset")
            length = files[file].get("length")
            print(f"[*] inflating {directory}/{file}")
            i = 0
            while i < length:
                x = content[offset + i] ^ ord(key[j % len(key)])
                if x == 0:
                    x = content[offset + i]
                if content[offset + i] == 0:
                    x = 0
                f.write(bytes([x]))
                i += 1
                j += 1
```

Then:

```
➜  _extracted_archive.nsar ls
a.out        e.gif     hdu.png      ok.mp3          s.gif      santaflag.pdf  ttt.gif
bbb.mp4      flag.odt  j.gif        okbro.png       sad.gif    santazic.mp3  twerk.gif
cd.gif       fr.gif    mario.gif    papanoel.png    santa.bmp  secret.jpg     udt.jpg
dlpmjcc.wmv  h.gif     nothing.png  real_santa.png  santa.gif  tkt.avi        yu.png
```

The flag can now be retrieved from `santaflag.pdf`:

![NSAR](/assets/santa/nsar/flag.png)

Thanks to [@Shutdown](https://twitter.com/@_nwodtuhs) and
[@Oik=](https://twitter.com/@Oik_eq) for this nice challenge!