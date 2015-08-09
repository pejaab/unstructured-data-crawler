import mysql.connector

class Dao(object) :

    #default database configuration
    _user = 'root'
    _passwd = 'idp2015'
    _host = '46.38.236.133'
    _db = 'impudo'

    _table_template = 'interface_templateitem'
    _table_record = 'interface_record'
    _table_rules = 'impudo_rules'

    # def __init__(self):
    #     self.conn = mysql.connector.connect(user='root', passwd='idp2015', host='46.38.236.133', database='impudo')
    #     self.cursor = self.conn.cursor()

    def __init__(self, user=_user, passwd=_passwd, host=_host, db=_db):
        self.conn = mysql.connector.connect(user=user, passwd=passwd, host=host, database=db)
        self.cursor = self.conn.cursor()

    #get xpath for site
    def get_path(self, url):
        sql = 'SELECT xpath, template_id from interface_crawler where url like "%{0}%" and active=1 limit 1'.format(url)
        return self.query_sql(sql)

    def get_rules(self, url):
        sql = 'SELECT follow_rules, parse_rules, follow_rules_deny, parse_rules_deny from impudo_rules where domain = "{0}" limit 1'.format(url)
        return self.query_sql(sql)


    '''def get_template(self):
        sql = 'SELECT id, url, desc from {0} limit 1'.format(self._table_template);
        return self.query_sql(sql)

    def update_path(self, id, path):
        sql = 'UPDATE {0} SET path="{1}" where id={2}'.format(self._table_template, path, id)
        self.execute_sql(sql) '''

    def insert_record(self, title, url, result, template_id):
        result = result.replace('\'', '\'\'')
        title = title.replace('\'', '\'\'')

        sql = "INSERT INTO {0} (title, url, result, template_id) VALUES ('{1}', '{2}', '{3}',{4})".format(self._table_record, title, url, result, template_id)
        self.execute_sql(sql)

    def insert_rule(self,domain, follow_rules, parse_rules, follow_rules_deny, parse_rules_deny):
        sql = "INSERT INTO {0} (domain, follow_rules, parse_rules, follow_rules_deny, parse_rules_deny) VALUES ('{1}', '{2}', '{3}','{4}', '{5}')".format(self._table_rules, domain, follow_rules, parse_rules, follow_rules_deny, parse_rules_deny)
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
