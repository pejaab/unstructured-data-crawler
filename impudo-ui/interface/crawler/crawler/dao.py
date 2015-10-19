import MySQLdb 

class Dao(object) :

    #default database configuration
    _user = 'root'
    _passwd = 'idp2015'
    _host = '46.38.236.133'
    #_host = 'localhost'
    _db = 'impudo'

    _table_template = 'interface_template'
    _table_record = 'interface_record'
    _table_record_details = 'interface_record_details'
    _table_image = 'interface_image'
    _table_crawlerimg = 'interface_crawlerimg'
    _table_crawler = 'interface_crawler'
    _table_rules = 'impudo_rules'

    # def __init__(self):
    #     self.conn = MySQLdb.connect(user='root', passwd='idp2015', host='46.38.236.133', db='impudo')
    #     self.cursor = self.conn.cursor()

    def __init__(self, user=_user, passwd=_passwd, host=_host, db=_db):
        self.conn = MySQLdb.connect(user=user, passwd=passwd, host=host, db=db, use_unicode=True, charset='utf8')
        self.cursor = self.conn.cursor()

    #get xpath for site
    #def get_path(self, url):
    #    sql = 'SELECT xpath, template_id from interface_crawler where url like "%{0}%" and active = 1'.format(url)
    #    self.cursor.execute(sql)
    #    return self.cursor

    def get_desc_xpath(self, template_id):
        sql = 'SELECT xpath from {0} where template_id={1} and active = 1 order by id asc'.format(self._table_crawler, template_id)
        self.cursor.execute(sql)
        return self.cursor

    def get_img_xpath(self, template_id):
        sql = 'SELECT xpath from {0} where template_id={1}'.format(self._table_crawlerimg, template_id)
        return self.query_sql(sql)

    def get_rules(self, url):
        sql = 'SELECT follow_rules, parse_rules, follow_rules_deny, parse_rules_deny, follow_xpath_restrict from {0} where domain = "{1}" limit 1'.format(self._table_rules, url)
        return self.query_sql(sql)

    def get_url(self, template_id):
        sql = 'SELECT url from {0} where id={1}'.format(self._table_template, template_id)
        return self.query_sql(sql)

    def insert_image(self, url, path, record_id):
        sql = "INSERT INTO {0} (url, path, record_id) VALUES ('{1}', '{2}', {3})".format(self._table_image, url, path, record_id)
        self.execute_sql(sql)

    def get_last_insert_id(self):
        return self.query_sql("SELECT LAST_INSERT_ID()")

    '''def get_template(self):
        sql = 'SELECT id, url, desc from {0} limit 1'.format(self._table_template);
        return self.query_sql(sql)

    def update_path(self, id, path):
        sql = 'UPDATE {0} SET path="{1}" where id={2}'.format(self._table_template, path, id)
        self.execute_sql(sql) '''

    def insert_record(self, title, url, result, template_id, price, dimensions):
        result = result.replace('\'', '\'\'')
        title = title.replace('\'', '\'\'')

        sql = "INSERT INTO {0} (title, url, result, template_id, price, dimensions) VALUES ('{1}', '{2}', '{3}',{4}, '{5}', '{6}')".format(self._table_record, title, url, result, template_id, price, dimensions)
        self.execute_sql(sql)

    def insert_image(self, path, record_id):
        sql = "INSERT INTO {0} (path, record_id) VALUES ('{1}', {2})".format(self._table_image, path, record_id)
        self.execute_sql(sql)

    def insert_rule(self,domain, follow_rules, parse_rules, follow_rules_deny, parse_rules_deny):
        sql = "INSERT INTO {0} (domain, follow_rules, parse_rules, follow_rules_deny, parse_rules_deny) VALUES ('{1}', '{2}', '{3}','{4}', '{5}')".format(self._table_rules, domain, follow_rules, parse_rules, follow_rules_deny, parse_rules_deny)
        self.execute_sql(sql)

    def execute_sql(self, sql):
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except MySQLdb.Error as e:
            self.conn.rollback()
            print("Error %d: %s" % (e.args[0], e.args[1]))

    def query_sql(self, sql):
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchone()
        except MySQLdb.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
