# dump_sagas  (c)2022..2023  Henrique Moreira

""" Interaction 'sagas'
"""

# pylint: disable=missing-function-docstring

import sys
import jdba
from copy import deepcopy

IO_ENCODING = "ISO-8859-1"

BASE_REL_DNAME = "../vidlib"


def main():
    if runner(sys.argv[1:]) is None:
        print("""Usage:
{__file__} command

Commands are:
   a           ASCII based dump
   b           New 'CampSov57'
   d           Dump 'sagas'
   s           Save database
""")

def runner(args, debug=0):
    param = args if args else ["d"]
    what = param[0]
    del param[0]
    if what not in "abds":
        return None
    opts = {}
    return do_this(what, param, opts, debug)

def do_this(what, param, opts, debug=0):
    assert not opts
    assert not param
    is_ok, infos, dbx = get_db()
    assert is_ok, dbx.name
    #dbx.set_db_save("d")  # Write database if different
    if not is_ok:
        print("Invalid paths:", dbx.path_refs())
        return None
    if what == "s":
        res = dbx.save()
        print("dbx.save():", res)
        return dbx.table_names()
    if what == "b":
        enter_new_item(dbx, dbx.table("sagas"))
    res = my_script(what, dbx, infos, debug)
    enc = jdba.jcommon.SingletonIO().default_encoding
    if what == "a":
        with open("sagas.tsv", "w", encoding=enc) as fdout:
            dump_out(fdout, res)
    return res


def my_script(what, dbx, infos, debug=0):
    assert len(what) == 1, what
    print(f"my_script(what='{what}', {dbx.name})")
    jix = dbx.table("sagas").dlist.index
    if debug > 0:
        print(jix.byname, end="\n" + "=" * 20 + "\n\n")
    a_case = "CampSov57"
    res = iterate_throu(dbx, jix, a_case)
    return res


def iterate_throu(dbx, jix, a_case):
    assert dbx, dbx.name
    marker_id = {}
    # Read markers
    for item in jix.get_ptr("Markers"):
        fcase = item["FCase"]
        if fcase and fcase == a_case:
            marker_id[item["FId"]] = item["FTime"]
    # Iterate throu
    seq = jix.get_ptr(a_case)
    res = []
    for item in seq:
        an_id = item["Id"]
        if an_id <= 0:
            break
        this = item
        assert 10 < len(this["Watch"]) < 20, f"Id={an_id} invalid watch"
        watch = "https://www.youtube.com/watch?v=" + this["Watch"]
        if an_id in marker_id:
            astr = youtube_minutes(marker_id[an_id])
            watch += f"&t={astr}"
        this["Watch"] = watch
        print(item)
        res.append(
            (
                str(item["Id"]),
                item["Watch"],
                item["Name"],
                item["UDesc"],
            )
        )
    return res


def enter_new_item(dbx, tbl):
    a_case = "CampSov57"
    new = deepcopy(tbl.dlist.get_case(a_case)[-1])
    new["Name"] = "NEW!"
    print("::: add_to():", new)
    tbl.add_to(a_case, new)
    print(tbl)
    return new


def dump_out(fdout, seq):
    for tup in seq:
        there = '\t'.join(tup)
        fdout.write(there + "\n")


def youtube_minutes(astr:str) -> str:
    """ Returns 12m56s if input 'astr' has a colon (e.g. 12:56)
    """
    assert isinstance(astr, str)
    if ":" not in astr:
        return astr
    spl = astr.split(":", maxsplit=2)
    if len(spl) == 2:
        return spl[0] + "m" + spl[1] + "s"
    return spl[0] + "h" + spl[1] + "m" + spl[2] + "s"


def get_db(debug=0) -> tuple:
    """ Open/ read database
    infos = {
        "main-cases": my_dlist.index.do_id_hash(),
        "main-dlist": my_dlist,
    }
    """
    print("# Reading dir:", BASE_REL_DNAME)
    dbx = jdba.database.Database(BASE_REL_DNAME, encoding=IO_ENCODING)
    is_ok = dbx.valid_schema(debug=debug)
    dbx.index_all()
    my_dlist = dbx.table("sagas").dlist
    my_dlist.index.do_id_hash()
    infos = {}
    return is_ok, infos, dbx


# Main script
if __name__ == "__main__":
    main()
