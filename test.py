# encoding: utf-8

'''

@author: ZiqiLiu


@file: test.py

@time: 2018/1/26 下午1:52

@desc:
'''
from XMLParser import XMLNode

if __name__ == '__main__':
    test_snippet = """<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE xml> <!-- not actually valid xml-->
        <!-- This is a comment -->
        <note date="8/31/12">
            <to>Tove</to>
            <from>Jani</from>
            <heading type="Reminder"/>
            <body>Don't forget me this weekend!</body>
            <!-- This is a multiline comment,
                 which take a bit of care to parse -->
        </note>
        """

    root = XMLNode(test_snippet, {}, "")
    print("root.tag: ", root.tag)
    print("root.attributes: ", root.attributes)
    print("root.content: ", str(root))
    print("root.children: ", root.children)
    print("")
    print("note.tag: ", root.children[0].tag)
    print("note.attributes: ", root.children[0].attributes)
    print("note.content: ", str(root.children[0]))
    print("note.children: ", root.children[0].children)

