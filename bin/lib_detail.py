#-*- coding: utf-8 -*

USAGE = '''
    ParserDetail lib
'''

INPUT_CODE = 'gbk'                  # html encode
OUTPUT_CODE = 'utf-8'               # output encode for databases


import os
import re
import urllib2


CATEGORIES = {
    "recom": '内容推荐',
    "index": '目录',
    }

P_CONTENT = re.compile(r'<textarea style="height:0px;border-width:0px;">\s*(?P<content>.*)\s*', re.DOTALL)


# Return utf-8 encode content
def fetchDangDang(dangdang_id, cache_dir, input_code):
    url = "http://product.dangdang.com/%s.html" % dangdang_id
    con = ''
    err = ''

    cache_path = ''
    if cache_dir:
        cache_path = os.path.join(cache_dir, "%s.html" % dangdang_id)
    if cache_path:
        if os.path.isfile(cache_path):
            con = open(cache_path).read()
            con = con.decode(input_code)
            con = con.encode('utf-8')

    if not con:
        try:
            con_r = urllib2.urlopen(url)
            con = con_r.read()
            if cache_path:
                open(cache_path, "wb").write(con)
            con = con.decode(input_code)
            con = con.encode('utf-8')
        except Exception as e:
            err = e

    return (con, err)


# convert a dangdang item id to details
def ParserDetail(dangdang_id, cache_dir, out_code=OUTPUT_CODE):

    ret = {}
    (content, err) = fetchDangDang(dangdang_id, cache_dir, INPUT_CODE)

    for key in CATEGORIES:
        con = ''
        word = CATEGORIES[key]
        s = content.find(word)
        if s != -1:
            tmp = content[s:]
            e = tmp.find("</textarea>")
            if e != -1:
                tmp = tmp[0:e].rstrip()
                p = P_CONTENT.search(tmp)
                if p:
                    con = p.group("content")
        con = con.decode('utf-8')
        con = con.encode(OUTPUT_CODE)
        ret[key] = con

    return (ret, err)


# test
if __name__ == "__main__":
    (res, err) = ParserDetail("22640661", "cache")
    if err:
        print err
    else:
        open("test.txt", "w").write("\n".join(["[%s]:\n%s" % (x, res[x]) for x in res]))
