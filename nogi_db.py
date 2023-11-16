import sqlite3


class NogiDB:
    def __init__(self, dbname):
        self.dbname = dbname
        
        
    def create_table(self):
        db_connect = sqlite3.connect(self.dbname)
        
        self.create_user_table(db_connect)
        self.create_user_info(db_connect)
        self.create_user_calendar(db_connect)
        
        db_connect.close()
        
    def insert_data(self, data, data_type):
        db_connect = sqlite3.connect(self.dbname)
        
        if (data_type == "user"):
            for user in data:
                self.insert_user(db_connect, user)
        
        db_connect.close()
        
        
    @staticmethod
    def insert_user(db_connect, user_data):
        """
        Userテーブルにデータを挿入します。
        user_data: (ID, Name) のタプル
        """
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
        'CREATE TABLE user(id INTEGER, name STRING, name_kn, birthday STRING, blood STRING, sign STRING)'

        """
        sql = ''' INSERT INTO UserInfo(ID, Name, Name_kn, BirthDay, Blood, Sign)
                VALUES(?, ?, ?, ?) '''
        cur = db_connect.cursor()
        cur.execute(sql, user_info_data)
        db_connect.commit()
        return cur.lastrowid
    
    @staticmethod
    def insert_user_calendar(self, db_connect, user_calendar_data):
        """
        UserCalendarテーブルにデータを挿入します。
        user_calendar_data: (ID, Date, Start Time, End Time, Category, Title) のタプル
        """
        sql = ''' INSERT INTO UserCalendar(ID, Date, StartTime, EndTime, Category, Title)
                VALUES(?, ?, ?, ?, ?, ?) '''
        cur = db_connect.cursor()
        cur.execute(sql, user_calendar_data)
        db_connect.commit()
        return cur.lastrowid
    
    def get_id(self, db_connect, name):
        """
        指定された名前に基づいてユーザーのIDを取得します。
        name: ユーザーの名前
        """
        sql = ''' SELECT ID FROM User WHERE Name = ? '''
        cur = db_connect.cursor()
        cur.execute(sql, (name,))
        row = cur.fetchone()
        if row:
            return row[0]
        return None
  
    def get_user(self, db_connect, user_id):
        """
        指定されたIDに基づいてUserテーブルからユーザーを取得します。
        user_id: ユーザーのID
        """
        sql = ''' SELECT * FROM User WHERE ID = ? '''
        cur = db_connect.cursor()
        cur.execute(sql, (user_id,))
        rows = cur.fetchall()
        return rows

        
    def get_user_info(self, db_connect, user_id):
        """
        指定されたIDに基づいてUserInfoテーブルからユーザー情報を取得します。
        user_id: ユーザーのID
        """
        sql = ''' SELECT * FROM UserInfo WHERE ID = ? '''
        cur = db_connect.cursor()
        cur.execute(sql, (user_id,))
        rows = cur.fetchall()
        return rows
    
    def get_user_calendar(self, db_connect, user_id):
        """
        指定されたIDに基づいてUserInfoテーブルからユーザー情報を取得します。
        user_id: ユーザーのID
        """
        sql = ''' SELECT * FROM UserInfo WHERE ID = ? '''
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
            'CREATE TABLE IF NOT EXISTS user_calendar(id INTEGER, start DATE, end DATE, category STRING, title STRING)'
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