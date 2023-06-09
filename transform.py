import sys
import os
from xml.etree import ElementTree

tree = ElementTree.parse(sys.argv[1])

device = tree.getroot()

known = {}

os.mkdir(device.find("name").text)
os.chdir(device.find("name").text)

for thing in device.findall("./peripherals/peripheral"):
    tname = thing.find("name")

    base = thing.find("baseAddress").text

    f = open(f"{tname.text}.py", "w")
    f.write("import uctypes\n\n")

    for cluster in thing.findall("./registers/cluster"):
        cname = cluster.find("name").text
        cdim = cluster.find("dim")

        if cdim is None:
            continue

        assert "[%s]" in cname
        cname = cname.replace("[%s]", "")
        f.write("%s = {\n" % cname)

        for register in cluster.findall("register"):
            name = register.find("name")
            dim = register.find("dim")
            size = register.find("size").text
            offset = register.find("addressOffset").text
            if dim is None:
                assert not "%s" in name.text
                f.write(f'    "{name.text}": {offset} | uctypes.UINT{size},\n')
            else:
                assert "%s" in name.text
                text = name.text.replace("[%s]", "")
                f.write(
                    f'    "{text}": ({offset} | uctypes.ARRAY, {dim.text} | uctypes.UINT{size}),\n'
                )

        f.write("}\n\n")

    f.write("%s = {\n" % tname.text)
    known[tname.text] = thing

    if thing.get("derivedFrom"):
        assert thing.get("derivedFrom") in known
        thing = known[thing.get("derivedFrom")]

    for register in thing.findall("./registers/register"):
        name = register.find("name")
        dim = register.find("dim")
        size = register.find("size").text
        offset = register.find("addressOffset").text
        if dim is None:
            assert not "%s" in name.text
            f.write(f'    "{name.text}": {offset} | uctypes.UINT{size},\n')
        else:
            assert "%s" in name.text
            text = name.text.replace("[%s]", "")
            f.write(
                f'    "{text}": ({offset} | uctypes.ARRAY, {dim.text} | uctypes.UINT{size}),\n'
            )

    for cluster in thing.findall("./registers/cluster"):
        cname = cluster.find("name").text
        cdim = cluster.find("dim")

        if not cdim is None:
            offset = cluster.find("addressOffset").text
            text = cname.replace("[%s]", "")
            f.write(f'    "{text}": ({offset} | uctypes.ARRAY, {cdim.text}, {text}),\n')
            continue

        for register in cluster.findall("register"):
            name = register.find("name")
            dim = register.find("dim")
            size = register.find("size").text
            offset = register.find("addressOffset").text
            if dim is None:
                assert not "%s" in name.text
                f.write(f'    "{name.text}": {offset} | uctypes.UINT{size},\n')
            else:
                assert "%s" in name.text
                text = name.text.replace("[%s]", "")
                f.write(
                    f'    "{text}": ({offset} | uctypes.ARRAY, {dim.text} | uctypes.UINT{size}),\n'
                )
    f.write("}\n\n")
    f.write(
        f"{tname.text.lower()} = uctypes.struct({base}, {tname.text}, uctypes.LITTLE_ENDIAN)\n"
    )
    f.close()
