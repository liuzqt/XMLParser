# encoding: utf-8

'''

@author: ZiqiLiu


@file: XMLParser.py

@time: 2018/1/25 上午10:26

@desc:
'''

import re
from collections import namedtuple

tag_open = re.compile(r"<([^!?/\s>]*)(( \S+=[\"\'].*?[\"\'])*?)/?>")
tag_close = re.compile(r"</([^\s>]*)>")
tag_open_close = re.compile(r"<([^!?/\s]*)(( \S+=[\"\'].*?[\"\'])*?)/>")
comment = re.compile(r"<!--(.*?)-->", re.S)
xml_prolog = re.compile(r"<\?([^>]*)\?>")
html_declaration = re.compile(r"<!([^>]*)(?<!--)>")

attr_pt = re.compile(r"(\S+)=[\"\'](.*?)[\"\']")

node = namedtuple('node', ['span', 'attr', 'tag', 'type'])


# type 0: open 1: close 2: open-close


class XMLNode:
    def __init__(self, raw_text, text=None, attributes=None, tag=None,
                 nodes=None):

        self.tag = tag
        self._attributes = attributes if attributes is not None else {}
        self._children = []
        self._raw_text = raw_text
        self._text = text
        if nodes is None:
            # root
            self._text = self._raw_text
            tags = []
            for t in tag_open.finditer(raw_text):
                attr = self._get_attrs(t.group(2))
                tags.append(node(span=t.span(), attr=attr, tag=t.group(1),
                                 type=2 if tag_open_close.match(
                                     t.group(0)) else 0))

            for t in tag_close.finditer(raw_text):
                tags.append(
                    node(span=t.span(), attr={}, tag=t.group(1), type=1))

            tags = sorted(tags, key=lambda i: i.span[0], reverse=True)
        else:
            tags = nodes

        stack = []
        descendants = []
        while len(tags) > 0:
            cur = tags.pop()
            if cur.type == 2:
                # open-close
                if len(stack) == 0:
                    self._children.append(
                        XMLNode('', raw_text, cur.attr, cur.tag))
                else:
                    descendants.append(cur)
            elif cur.type == 0:
                # open
                stack.append(cur)
                descendants.append(cur)
            else:
                # close
                if len(stack) == 0:
                    raise Exception(
                        "invalid! close tag <%s> without open" % cur.tag)
                if stack[-1].tag != cur.tag:
                    raise Exception('invalid! <%s> closed with </%s>' % (
                        stack[-1].tag, cur.tag))
                start = stack.pop()
                end = cur
                if len(stack) == 0:
                    temp = list(reversed(descendants[1:])) if len(
                        descendants) > 0 else []
                    descendants = []
                    sub_content = raw_text[start.span[-1]:end.span[0]]
                    self._children.append(
                        XMLNode(sub_content, raw_text, start.attr, start.tag,
                                temp))
                else:
                    descendants.append(cur)
        if len(stack) > 0:
            raise Exception('invalid! tag <%s> without close', stack[-1].tag)

    def _get_attrs(self, attrs_str):
        attrs = {}
        if len(attrs_str) > 0:
            attrs_list = attr_pt.findall(attrs_str)
            for key, val in attrs_list:
                attrs[key] = val
        return attrs

    @property
    def children(self):
        return self._children

    @property
    def attributes(self):
        return self._attributes

    def find(self, tag, **kwargs):
        """
        find the first occurrence of given condition 
        :param tag: 
        :param kwargs: 
        :return: node found
        """
        self._clean_kwargs(kwargs)

        stack = [i for i in reversed(self._children)]

        while len(stack) > 0:
            node = stack.pop()
            if node.tag == tag:
                skip = False
                for k, v in kwargs.items():
                    if k not in node.attributes or node.attributes[k] != v:
                        skip = True
                        break
                if not skip:
                    return node
            stack.extend([i for i in reversed(node.children())])

        return None

    def find_all(self, tag, **kwargs):
        """
                find all occurrences of given condition, 
                return empty list if not found
                :param tag: 
                :param kwargs: 
                :return: list of node found
                """
        self._clean_kwargs(kwargs)
        res = []
        stack = [i for i in reversed(self._children)]

        while len(stack) > 0:
            node = stack.pop()
            if node.tag == tag:
                skip = False
                for k, v in kwargs.items():
                    if k not in node.attributes or node.attributes[k] != v:
                        skip = True
                        break
                if not skip:
                    res.append(node)
            stack.extend([i for i in reversed(node.children())])

        return res

    def text(self):
        return self._text

    def __str__(self):
        return self._text

    def __getattr__(self, item):
        for c in self._children:
            if c.tag == item:
                return c
        raise Exception('child node %s not found' % str(item))

    def __getitem__(self, item):
        if not isinstance(item, str):
            raise Exception('can only use str as attr key! got %s instead.',
                            type(item))
        if item in self._attributes:
            return self._attributes[item]
        else:
            raise Exception('attr %s not found!' % item)

    def _clean_kwargs(self, kwargs):
        if 'class_' in kwargs:
            kwargs['class'] = kwargs['class_']
            del kwargs['class_']
