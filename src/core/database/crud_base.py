import sqlite3
from core.database.database import get_connection

class CRUDBase:
    table_name = ""

    @classmethod
    def create(cls, **kwargs):
        columns = ', '.join(kwargs.keys())
        placeholders = ', '.join(['?' for _ in kwargs])
        values = tuple(kwargs.values())

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f'''
            INSERT INTO {cls.table_name} ({columns})
            VALUES ({placeholders})
        ''', values)
        conn.commit()
        conn.close()

    @classmethod
    def get_by_id(cls, id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM {cls.table_name} WHERE id = ?', (id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return cls(*row)
        return None

    @classmethod
    def update(cls, id, **kwargs):
        set_clause = ', '.join([f"{key} = ?" for key in kwargs])
        values = tuple(kwargs.values()) + (id,)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f'''
            UPDATE {cls.table_name}
            SET {set_clause}
            WHERE id = ?
        ''', values)
        conn.commit()
        conn.close()

    @classmethod
    def delete(cls, id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f'DELETE FROM {cls.table_name} WHERE id = ?', (id,))
        conn.commit()
        conn.close()

    @classmethod
    def execute_query(cls, query, params=()):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.commit()
        conn.close()
        return results