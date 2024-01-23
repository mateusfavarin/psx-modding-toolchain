from glob import glob

files = glob("*/*.c") + glob("*/*.s")
files = [file.replace("\\", "/") for file in files]
libs = {}
buffer = ""

for file in files:
    lib, filename = file.split("/")
    obj_file = lib + "_" + filename[:-2] + ".o"
    if lib in libs:
        libs[lib].append(obj_file)
    else:
        libs[lib] = [obj_file]
    buffer += obj_file + ": " + file + "\n"
    buffer += "\t" + "$(CC) $(CPPFLAGS) -c -o $@ $^\n\n"

for key in libs:
    objs = libs[key]
    buffer += key + ".a: " + " ".join(objs) + "\n"
    buffer += "\t" + "$(AR) rcs lib/$@ $^\n\n"

print(buffer)