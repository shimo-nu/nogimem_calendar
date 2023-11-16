import sqlite3
from functools import wraps

def with_db_connection(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        db_connect = sqlite3.connect(self.dbname)
        try:
            return func(self, db_connect, *args, **kwargs)
        finally:
            db_connect.close()
    return wrapper

class NogiDB:
    def __init__(self, dbname):
        self.dbname = dbname
        
    def __enter__(self):
        db_connect = sqlite3.connect(self.dbname)
        self.db_connect = db_connect
        return self
    
    def __exit__(self, exception_type, exception_value, traceback):
        self.db_connect.close()
        
    @with_db_connection
    def create_table(self, db_connect):
        
        self.create_user_table(db_connect)
        self.create_user_info(db_connect)
        self.create_user_calendar(db_connect)
        
    @with_db_connection
    def insert_data(self, db_connect, data, data_type):
        
        if (data_type == "user"):
            for user in data:
                self.insert_user(db_connect, user)

  
        
        
        
    @staticmethod
    def insert_user(db_connect, user_data):
        """
        Userテーブルにデータを挿入します。
        user_data: (Name, URL) のタプル
        IDはAutoIncrement
        """
        
         # まずはユーザー名が既に存在するか確認
        cur = db_connect.cursor()
        cur.execute("SELECT * FROM User WHERE Name = ?", (user_data[0],))
        if cur.fetchone():
            return None

        sql = ''' INSERT INTO User(Name, Url)
                VALUES(?, ?) '''
        cur = db_connect.cursor()
        cur.execute(sql, user_data)
        db_connect.commit()
        return cur.lastrowid

    @staticmethod
    def insert_user_info(db_connect, user_info_data):
        """
        UserInfoテーブルにデータを挿入します。
        user_info_data: (ID, Name, Name1, Name2) のタプル
        'CREATE TABLE user_info(id INTEGER, name STRING, name_kn, birthday STRING, blood STRING, sign STRING)'

        """
        sql = ''' INSERT INTO UserInfo(ID, Name, Name_kn, BirthDay, Blood, Sign)
                VALUES(?, ?, ?, ?) '''
        cur = db_connect.cursor()
        cur.execute(sql, user_info_data)
        db_connect.commit()
        return cur.lastrowid
    
    @staticmethod
    def insert_user_calendar(db_connect, user_calendar_data):
        """
        UserCalendarテーブルにデータを挿入します。
        user_calendar_data: (ID, Date, Start, End, Category, Title) のタプル
        同じTitleとDateのデータが存在しない場合のみ挿入します。
        """
        # 既に同じTitleとDateのデータが存在するか確認
        check_sql = ''' SELECT COUNT(*) FROM user_calendar WHERE Date = ? AND Title = ? '''
        cur = db_connect.cursor()
        cur.execute(check_sql, (user_calendar_data[1], user_calendar_data[5]))
        exists = cur.fetchone()[0] > 0

        if not exists:
            # データが存在しない場合のみ挿入
            insert_sql = ''' INSERT INTO user_calendar(ID, Date, Start, End, Category, Title)
                            VALUES(?, ?, ?, ?, ?, ?) '''
            cur.execute(insert_sql, user_calendar_data)
            db_connect.commit()
            return cur.lastrowid
        else:
            # 既に存在する場合は何もしない
            return None

    
    @staticmethod
    def get_id(db_connect, name):
        """
        指定された名前に基づいてユーザーのIDを取得します。
        name: ユーザーの名前
        """
        sql = ''' SELECT ID FROM user WHERE Name = ? '''
        cur = db_connect.cursor()
        cur.execute(sql, (name,))
        row = cur.fetchone()
        if row:
            return row[0]
        return None
    
    @staticmethod
    def get_user(db_connect, user_id):
        """
        指定されたIDに基づいてUserテーブルからユーザーを取得します。
        user_id: ユーザーのID
        """
        sql = ''' SELECT * FROM user WHERE ID = ? '''
        cur = db_connect.cursor()
        cur.execute(sql, (user_id,))
        rows = cur.fetchall()
        return rows

    @staticmethod
    def get_all_user(db_connect):
        
        sql = ''' SELECT * FROM user '''
        cur = db_connect.cursor()
        cur.execute(sql, ())
        rows = cur.fetchall()
        return rows

    @staticmethod
    def get_user_info(db_connect, user_id):
        """
        指定されたIDに基づいてUserInfoテーブルからユーザー情報を取得します。
        user_id: ユーザーのID
        """
        sql = ''' SELECT * FROM user_info WHERE ID = ? '''
        cur = db_connect.cursor()
        cur.execute(sql, (user_id,))
        rows = cur.fetchall()
        return rows
    
    def get_user_calendar(self, db_connect, user_id):
        """
        指定されたIDに基づいてUserInfoテーブルからユーザー情報を取得します。
        user_id: ユーザーのID
        """
        sql = ''' SELECT * FROM user_calendar WHERE ID = ? '''
        cur = db_connect.cursor()
        cur.execute(sql, (user_id,))
        rows = cur.fetchall()
        return rows



    @staticmethod
    def create_user_table(db_con):
        cur = db_con.cursor()
        
        cur.execute(
            'CREATE TABLE IF NOT EXISTS user(id INTEGER PRIMARY KEY AUTOINCREMENT, name STRING, url STRING)'
        )
        
        db_con.commit()
    @staticmethod
    def create_user_info(db_con):
        cur = db_con.cursor()
        
        cur.execute(
            'CREATE TABLE IF NOT EXISTS user_info(id INTEGER, name STRING, name_kn, birthday STRING, blood STRING, sign STRING)'
            
        )

        db_con.commit()
        
    @staticmethod
    def create_user_calendar(db_con):
        cur = db_con.cursor()
        
        cur.execute(
            'CREATE TABLE IF NOT EXISTS user_calendar(id INTEGER, date DATE, start DATE, end DATE, category STRING, title STRING)'
        )

        db_con.commit()
        
    @staticmethod
    def table_isexist(db_con):
        cur = db_con.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM sqlite_master 
            WHERE TYPE='table' AND name='<テーブル名>'
            """)
        if cur.fetchone()[0] == 0:
            return False
        return True  
        
if __name__=='__main__':
    dbname = 'TEST.db'
    db = NogiDB(dbname)
    db.create_table()

    # userdata = (0, "shimo")
    # db.insert_data(userdata)
    

# User Table
# ID | Name | URL 

# User Info
# ID | Name | Name 1 | Name 2 

# User Calendar
# ID | Date | Start Time | End Time | Category | Title |  