import sys
import os
from xml.etree import ElementTree

tree = ElementTree.parse(sys.argv[1])

device = tree.getroot()

known = {}

# TODO
# consider "./registers/cluster"

os.mkdir(device.find("name").text)
os.chdir(device.find("name").text)

for thing in device.findall("./peripherals/peripheral"):
    name = thing.find("name")
    f = open(f"{name.text}.py", "w")
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

    f.write("%s = {\n" % name.text)
    known[name.text] = thing
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

        if cdim:
            offset = cluster.find("addressOffset").text
            text = cname.replace("[%s]", "")
            f.write(f'    "{text}": ({offset} | uctypes.ARRAY, {dim.text} | cname),\n')
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
    f.write("}\n")
    f.close()
