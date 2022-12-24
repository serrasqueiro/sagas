# dump_sagas  (c)2022  Henrique Moreira

""" Interaction 'sagas'
"""

# pylint: disable=missing-function-docstring

import sys
from jdba.jbox import JBox
import jdba

def main():
    if runner(sys.argv[1:]) is None:
        print("""Usage:
{__file__} command

Commands are:
   d           Dump 'sagas'
""")

def runner(args, debug=0):
    param = args if args else ["d"]
    what = param[0]
    del param[0]
    opts = {}
    return do_this(what, param, opts, debug)

def do_this(what, param, opts, debug=0):
    is_ok, infos, dbx = get_db(debug=1)
    assert is_ok, dbx.name
    dbx.set_db_save("d")  # Write database if different
    if not is_ok:
        print("Invalid paths:", dbx.path_refs())
        return None
    assert not param
    res = my_script(what, dbx, infos)
    return res


def my_script(what, dbx, infos, debug=0):
    assert len(what) == 1, what
    print(f"my_script(what='{what}', {dbx.name})")
    jix = dbx.table("sagas").dlist.index
    if debug > 0:
        print(jix.byname, end="\n" + "=" * 20 + "\n\n")
    seq = jix.get_ptr("CampSov57")
    for item in seq:
        an_id = item["Id"]
        if an_id <= 0:
            break
        this = item
        assert 10 < len(this["Watch"]) < 20, f"Id={an_id} invalid watch"
        watch = "https://www.youtube.com/watch?v=" + this["Watch"]
        this["Watch"] = watch
        print(item)
    return []


def get_db(debug=0) -> tuple:
    """ Open/ read database
    infos = {
        "main-cases": my_dlist.index.do_id_hash(),
        "main-dlist": my_dlist,
    }
    """
    dbx = jdba.database.Database("../vidlib")
    is_ok = dbx.valid_schema()
    dbx.index_all()
    my_dlist = dbx.table("sagas").dlist
    my_dlist.index.do_id_hash()
    infos = {}
    return is_ok, infos, dbx


# Main script
if __name__ == "__main__":
    main()
