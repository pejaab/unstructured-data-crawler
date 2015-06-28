import MySQLdb

class Dao(object) :

    #default database configuration
    _user = 'root'
    _passwd = 'idp2015'
    _host = '46.38.236.133'
    _db = 'impudo'

    _table_template = 'interface_templateitem'
    _table_record = 'crawl_record'

    # def __init__(self):
    #     self.conn = MySQLdb.connect(user='root', passwd='idp2015', host='46.38.236.133', db='impudo')
    #     self.cursor = self.conn.cursor()

    def __init__(self, user=_user, passwd=_passwd, host=_host, db=_db):
        self.conn = MySQLdb.connect(user=user, passwd=passwd, host=host, db=db)
        self.cursor = self.conn.cursor()

    def get_template(self):
        sql = 'SELECT id, url, desc from {0} limit 1'.format(self._table_template);
        return self.query_sql(sql)

    def update_path(self, id, path):
        sql = 'UPDATE {0} SET path="{1}" where id={2}'.format(self._table_template, path, id)
        self.execute_sql(sql)

    def insert_record(self, url, result, template_id):
        result = result.replace('\'', '\'\'')
        sql = "INSERT INTO {0} (url, result, template_id) VALUES ('{1}', '{2}', {3})".format(self._table_record, url, result, template_id)
        self.execute_sql(sql)

    def execute_sql(self, sql):
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except MySQLdb.Error, e:
            self.conn.rollback()
            print "Error %d: %s" % (e.args[0], e.args[1])

    def query_sql(self, sql):
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchone()
        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])