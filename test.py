#!/usr/bin/env python
#-*-coding:utf-8-*-

import session


if __name__ == '__main__':
    m = session.SessionManager()

    s = m.new_session()
    print "session_id:%s" % s.session_id
    s['nickname'] = 'Yarkee'
    s['foo'] = 'bar'
    print "The length of session:%d" % len(s)

    if 'nickname' in s:
        print "nickname is %s" % s['nickname']
    print s

    del s['foo']

    s2 = m.get_session(s.session_id)
    print s2

