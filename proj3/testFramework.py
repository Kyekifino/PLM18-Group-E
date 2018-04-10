# vim: set filetype=python ts=2 sw=2 sts=2 expandtab:

import traceback, time, re

def about(f):
    print("\n-----| %s |-----------------" % f.__name__)
    if f.__doc__:
        print("# " + re.sub(r'\n[ \t]*', "\n# ", f.__doc__))

TRY = FAIL = 0

def testFramework(f=None):
    global TRY, FAIL
    if f:
        try:
            TRY += 1; about(f); f(); print("# pass");
        except:
            FAIL += 1; print(traceback.format_exc());
        return f
    else:
        print("\n# %s TRY= %s ,FAIL= %s ,%%PASS= %s" % (
            time.strftime("%d/%m/%Y, %H:%M:%S,"),
            TRY, FAIL,
            int(round((TRY - FAIL) * 100 / (TRY + 0.001)))))
