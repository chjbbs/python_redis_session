#! /usr/bin/env python
#-*-coding:utf-8-*-

__author__ = "iyarkee@gmail.com"

import datetime
import time
import hashlib
import os
try:
    import cPickle as pickle
except ImportError:
    import pickle
import redis


VARS = {
    'SESSION_EXPIRE_TIME': 86400,   # 1 day
    'REDIS_ADDR':{'ip':'127.0.0.1', 'port':6379, 'db':0}
}


class SessionManager(object):
    """Manager various session objects"""
    def __init__(self, session_expire_time = VARS['SESSION_EXPIRE_TIME'], 
            redis_addr = VARS['REDIS_ADDR']):
        self._session_expire_time = session_expire_time
        self._redis_conn = redis.StrictRedis(host = redis_addr['ip'], 
                port = redis_addr['port'], db = redis_addr['db'])

    def get_session(self, session_id):
        """Get session by session_id. If session not exists or expired, 
            return None. Else return the session
        """
        session_data = self._redis_conn.get(session_id)
        if session_data is None:
            return 
        try:
            session = pickle.loads(session_data)
        except Exception as e:
            self.del_session_by_id(session_id)
            return None
        if not isinstance(session, Session):
            self.del_session_by_id(session_id)
            return None
        session.refresh()
        return session
    
    def new_session(self, expire_time = None):
        """Make a new session.Return the session if succeed, 
            else return None
        """
        if expire_time:
            session = Session(expire_time)
        else:
            session = Session(self._session_expire_time)
        if self.save_session(session):
            return session
        else:
            return None

    def save_session(self, session):
        """save session to db"""
        data = pickle.dumps(session)
        return self._redis_conn.setex(session.session_id, 
                session.expire_time, data)

    def del_session_by_id(self, session_id):
        """delete session by session_id"""
        return self._redis_conn.delete(session_id)


class Session(object):
    """Session object"""
    def __init__(self, expire_time):
        self._session_id = self._new_session_id()
        self._expire_time = expire_time
        self._data = dict()

    def _new_session_id(self):
        """make a unique new session id"""
        return os.urandom(32).encode('hex')

    @property
    def session_id(self):
        return self._session_id

    @property
    def expire_time(self):
        return self._expire_time

    def refresh(self):
        self._update_time = int(time.time())
        return self._save()

    def has_key(self, key):
        return self._data.has_key(key)

    def _save(self):
        return SessionManager().save_session(self)

    def delete(self):
        return SessionManager().del_session_by_id(self.session_id)

    def __delitem__(self, key):
        del self._data[key]
        return self._save()

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value
        return self._save()

    def __len__(self):
        return len(self._data)

    def __contains__(self, key):
        return self._data.has_key(key)

    def __iter__(self):
        for key in self._data:
            yield key

    def __str__(self):
        value = ", ".join(['"%s" = "%s"' % 
            (k, self._data[k]) for k in self._data])
        return u"sid:%s, {%s}" % (self.session_id, value)
