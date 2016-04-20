import mysql.connector

class Dao(object) :

    #default database configuration
    _user = 'root'
    _passwd = 'idp2015'
    _host = '46.38.236.133'
    _db = 'impudo'

    _table_template = 'interface_template'
    _table_record = 'interface_crawler'

    # def __init__(self):
    #     self.conn = mysql.connector.connect(user='root', passwd='idp2015', host='46.38.236.133', database='impudo')
    #     self.cursor = self.conn.cursor()

    def __init__(self, user=_user, passwd=_passwd, host=_host, db=_db, port=_port):
        self.conn = mysql.connector.connect(user=user, passwd=passwd, host=host, port=port, database=db)
        self.cursor = self.conn.cursor()

    def get_template(self):
        sql = 'SELECT id, url, desc from {0} limit 1'.format(self._table_template);
        return self.query_sql(sql)

    def update_path(self, id, xpath):
        sql = 'UPDATE {0} SET xpath="{1}" where id={2}'.format(self._table_template, xpath, id)
        self.execute_sql(sql)

    def insert_record(self, template_id, xpath, content, url, active):
        xpath = xpath.replace('\'', '\'\'')
        sql = "INSERT INTO {0} (template_id, xpath, content, url, active) VALUES ('{1}', '{2}', {3})".format(self._table_record, template_id, xpath, content, url, active)
        self.execute_sql(sql)

    def execute_sql(self, sql):
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except mysql.connector.Error as e:
            self.conn.rollback()
            print("Error %d: %s" % (e.args[0], e.args[1]))

    def query_sql(self, sql):
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchone()
        except mysql.connector.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
