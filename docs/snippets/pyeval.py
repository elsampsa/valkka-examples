#!/usr/bin/python3
"""Script's first argument: input file
"""
import sys

def main():
    hide = False
    rst_mode = False
    empty = None # checks if found comment or code sections were empty or not
    leadspace = 0
    f = open(sys.argv[1])
    lines = []
    c = 0 # line counter
    last_csec = 0 # last line where a code section started
    inst = "    "
    newlines = []
    for line in f.readlines():
        st = line[:-1] # remove newline
        if st.strip().lower() in ["#<hide", "#</hide>"]:
            hide = False
            c+=1
            continue
        elif st.strip().lower() in ["#hide>", "#<hide>"]:
            hide = True
        if hide:
            c+=1
            continue
        if (c == 0 and st.strip() != '"""<rtf>'): 
            # first line and NOT starting with comment section
            # so start with code section
            """print("")
            print(".. code:: python")
            print("")
            print(inst+st)"""
            newlines +=  [
                "",
                ".. code:: python",
                "",
                inst+st
            ]
        elif (st.strip() == '"""<rtf>'): 
            # comment section starts
            # let's see how many empty lines we had in the prepending code section
            if empty:
                # new comment section starts but the previous code
                # section was empty .. so let's remote it
                for i in range(0, empty):
                    newlines.pop(-1)
            rst_mode = True
            # check how many leading spaces
            leadspace = len(st) - len(st.lstrip())
            # print("")
            newlines.append("")
            empty = 1 # only empty lines in this comment section for the moment
        elif (st.strip() == '<rtf>"""'): 
            # rtf comment section stops - start code section again
            if empty:
                # new code section starts but the previous comment
                # section was empty .. so let's remote it
                for i in range(0, empty):
                    newlines.pop(-1)
            last_csec=len(newlines)
            rst_mode = False
            """print("")
            print(".. code:: python")
            print("")"""
            newlines += [
                "",
                ".. code:: python",
                ""
            ]
            empty = 3 # only empty lines in this code section for the moment
        elif (rst_mode == False):
            # print into code section
            # print(inst+st)
            if (empty is not None) and len(st.strip()) == 0: # empty line in this code section
                empty += 1
            else:
                empty = None # ok.. all the lines were not empty
            newlines.append(inst+st)
        else:
            # print into comment section
            # print(st[leadspace:])
            if (empty is not None) and len(st.strip()) == 0: # empty line in this comment section
                empty += 1
            else:
                empty = None # ok.. all the lines were not empty
            newlines.append(st[leadspace:])
        c+=1

    if empty:
        # previous section was empty .. so let's remote it
        for i in range(0, empty):
            newlines.pop(-1)

    for line in newlines:    
        print(line)

if __name__ == "__main__":
    main()

