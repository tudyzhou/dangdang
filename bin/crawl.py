#! /usr/bin/env python

USAGE = '''
    USAGE:
        %s <id_lis.txt> <output.txt>
''' % __file__

import os
import sys
import re
import time
import urllib2

from lib_detail import ParserDetail


P_img = re.compile(r'img src=\'(.+\d+-1_l\.jpg)')
P_item = re.compile(r'/(\d{3,})-1_l\.jpg$')

def Debug(msg, out=sys.stderr):
    if out != sys.stderr:
        print >> out, msg
    print >> sys.stderr, msg


def parserDB(_f, debug):
    for line in open(_f):
        line = line.rstrip()
        if not line:
            continue
        if line[0] == "#":
            continue
        yield line


def fetchPIC(url, out_p, debug):
    img_url = re.sub(r'1_l.jpg$', '1_e.jpg', url)
    img = ''

    try:
        img_r = urllib2.urlopen(img_url)
        img = img_r.read()
        open(out_p, "wb").write(img)
    except Exception as e:
        Debug("[ERR] Fetch %s: %s" % (img_url, e))

    return len(img)


def fetchRecord(_id, img_out_p, debug):
    url = "http://search.dangdang.com/?key=%s" % _id

    try:
        response = urllib2.urlopen(url)
        html = response.read()
    except Exception as e:
        Debug("[ERR] Fetch %s: %s" % (url, e))

    ret = ''
    p = P_img.search(html)
    if p:
        ret = p.group(1)
        fetchPIC(ret, img_out_p, debug)
    
    return ret, url


def assertDir(_dir):
    if not os.path.isdir(_dir):
        os.mkdir(_dir)


def fetchDetail(img_url, cache_dir, debug):
    item_id = P_item.search(img_url).group(1)
    (ret, err) = ParserDetail(item_id, cache_dir)
    if err:
        Debug("[ERR] Fetch dangdang item %s FAIL. %s, %s" % (item_id, err, img_url), debug)

    return ret


def main(db_p, output_p):
    base_p = re.sub(r'\.txt', '', output_p)

    cache_p = "%s_cache" % (base_p)
    index_p = "%s_index" % (base_p)
    recom_p = "%s_recom" % (base_p)

    assertDir(base_p)
    assertDir(cache_p)
    assertDir(index_p)
    assertDir(recom_p)

    output = open(output_p, "w")
    debug_p = base_p + ".debug.txt"
    debug = open(debug_p, "w")

    r_fmt = lambda x: x if x else "-"
    output.write("#ID\timg\tindex\trecom\torg\n")

    for _id in parserDB(db_p, debug):

        img_out = os.path.join(base_p, "%s.jpg" % _id)
        index_out = os.path.join(index_p, "%s.txt" % _id)
        recom_out = os.path.join(recom_p, "%s.txt" % _id)
        if os.path.isfile(img_out) \
                and os.path.isfile(index_out) \
                and os.path.isfile(recom_out):
            Debug("[DETAIL] %s record exist in '%s', conitnue next" % (_id, img_out))
            continue

        details = {}
        matchs = [0,0,0]
        status = "FAIL"
        prefix = "ERR"
        start_t = time.time()
        (img_url, search_url) = fetchRecord(_id, img_out, debug)


        if img_url:
            status = "WARM"
            matchs[0] = 1

            details = fetchDetail(img_url, cache_p, debug)
            index_con = details.get("index", None)
            recom_con = details.get("recom", None)

            if index_con:
                matchs[1] = 1
                open(index_out, 'w').write(index_con)
            if recom_con:
                matchs[2] = 1
                open(recom_out, 'w').write(recom_con)

            if sum(matchs) == 3:
                status = "OK"
                prefix = "DETAIL"

        matchs = map(str, matchs)
        Debug("[%s] Fetch %s, %s %.2f second. %s " % (
            prefix, _id, '-'.join(matchs), time.time()-start_t, status), debug)

        output.write("%s\t%s\t%s\n" % (_id, '\t'.join(matchs), r_fmt(img_url)))

    
    debug.close()
    output.close()


if __name__ == "__main__":
    if len(sys.argv) == 3:
        main(*sys.argv[1:])
    else:
        print USAGE
