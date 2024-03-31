from pathlib import Path
from base58 import b58decode


PREFIXES = [["SoL", True]]
SUFFIX = ""

b58decode(SUFFIX)

# map of all possible versions of the prefix (both upper and lowercase for each letter)

def all_cases(string: str): 
    all_strings = [""]
    for char in string:
        new_strings = []
        for case in [char.lower(), char.upper()]:
            for s in all_strings:
                new_strings.append(s + case)
        all_strings = new_strings
    return all_strings

all_prefixes = set()
for prefix, ignore_case in PREFIXES:
    if ignore_case:
        all_prefixes.update(all_cases(prefix))
    else:
        all_prefixes.add(prefix)

valid_prefixes = []
all_prefix_bytes = list()
prefix_lens = []
skip_count = 0
for prefix in all_prefixes:
    try: 
        b58decode(prefix)
        prefix_bytes = bytes(prefix.encode())
        all_prefix_bytes.extend(prefix_bytes)
        prefix_lens.append(len(prefix_bytes))
        valid_prefixes.append(prefix)
    except Exception as e:
        skip_count += 1
        continue

print(f"Skipped {skip_count} invalid prefixes")
print(f"Valid prefixes: {len(prefix_lens)}")
SUFFIX_BYTES = list(bytes(SUFFIX.encode()))

Path(f"validPrefixes.txt").write_text("\n".join(map(str, valid_prefixes)))

with open("opencl/kernel.cl", "r") as f:
    source_lines = f.readlines()

for i, s in enumerate(source_lines):
    if s.startswith("constant uchar PREFIXES[]"):
        source_lines[i] = (
            f"constant uchar PREFIXES[] = {{{', '.join(map(str, all_prefix_bytes))}}};\n"
        )
        print("Succeed update prefixes in kernel file.")

    if s.startswith("constant size_t PREFIX_LENGTHS[]"):
        source_lines[i] = (
            f"constant size_t PREFIX_LENGTHS[] = {{{', '.join(map(str, prefix_lens))}}};\n"
        )
        print("Succeed update prefix lens in kernel file.")

    if s.startswith("constant size_t NUM_PREFIXES"):
        source_lines[i] = (
            f"constant size_t NUM_PREFIXES = {len(prefix_lens)};\n"
        )
        print("Succeed update num prefixes in kernel file.")

    if s.startswith("constant uchar SUFFIX[]"):
        source_lines[i] = (
            f"constant uchar SUFFIX[] = {{{', '.join(map(str, SUFFIX_BYTES))}}};\n"
        )
        print("Succeed update suffix in kernel file.")


with open("opencl/kernel.cl", "w") as f:
    f.writelines(source_lines)
