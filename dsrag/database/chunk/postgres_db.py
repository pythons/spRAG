import os
import time
from typing import Any, Optional

from dsrag.database.chunk.db import ChunkDB
from dsrag.database.chunk.types import FormattedDocument
from dsrag.utils.imports import LazyLoader
from dsrag.database.chunk.metadata_utils import (
    deserialize_metadata,
    serialize_metadata,
)

# Lazy load PostgreSQL dependencies
psycopg2 = LazyLoader("psycopg2", "psycopg2-binary")


class PostgresChunkDB(ChunkDB):

    def __init__(self, kb_id: str, username: Optional[str] = None, password: Optional[str] = None, database: Optional[str] = None, host: str="localhost", port: int = 5432) -> None:
        self.kb_id = kb_id
        self.username = username or os.environ.get("POSTGRES_USER")
        self.password = password or os.environ.get("POSTGRES_PASSWORD")
        self.database = database or os.environ.get("POSTGRES_DB")
        self.host = host or os.environ.get("POSTGRES_HOST", "localhost")
        self.port = port or int(os.environ.get("POSTGRES_PORT", 5432))

        if not self.username or not self.password or not self.database:
            raise ValueError(
                "PostgresChunkDB requires username, password, and database. "
                "Provide them directly or set POSTGRES_USER/POSTGRES_PASSWORD/POSTGRES_DB."
            )
        self.table_name = f"{kb_id}_documents"

        self.columns = [
            {"name": "doc_id", "type": "TEXT"},
            {"name": "document_title", "type": "TEXT"},
            {"name": "document_summary", "type": "TEXT"},
            {"name": "section_title", "type": "TEXT"},
            {"name": "section_summary", "type": "TEXT"},
            {"name": "chunk_text", "type": "TEXT"},
            {"name": "chunk_index", "type": "INT"},
            {"name": "chunk_length", "type": "INT"},
            {"name": "chunk_page_start", "type": "INT"},
            {"name": "chunk_page_end", "type": "INT"},
            {"name": "is_visual", "type": "BOOLEAN"},
            {"name": "created_on", "type": "TEXT"},
            {"name": "supp_id", "type": "TEXT"},
            {"name": "metadata", "type": "TEXT"},
        ]

        # Create a table for this kb_id if it doesn't exist
        conn = psycopg2.connect(
            dbname=self.database,
            user=self.username,
            password=self.password,
            host=self.host,
            port=self.port
        )
        cur = conn.cursor()
        from psycopg2 import sql
        cur.execute(
            sql.SQL(
                "SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = %s)"
            ),
            (self.table_name,),
        )
        exists = cur.fetchone()[0]

        if not exists:
            # Create a table for this kb_id
            query_statement = sql.SQL("CREATE TABLE {} (").format(sql.Identifier(self.table_name)).as_string(cur)
            for column in self.columns:
                query_statement += f"{column['name']} {column['type']}, "
            query_statement = query_statement[:-2] + ")"
            cur.execute(query_statement)
            conn.commit()
        else:
            # Check if we need to add any columns to the table. This happens if the columns have been updated
            cur.execute(
                "SELECT column_name FROM information_schema.columns WHERE table_name = %s",
                (self.table_name,),
            )
            columns = cur.fetchall()
            column_names = [column[0] for column in columns]
            for column in self.columns:
                if column["name"] not in column_names:
                    # Add the column to the table
                    cur.execute(
                        sql.SQL("ALTER TABLE {} ADD COLUMN {} {}").format(
                            sql.Identifier(self.table_name),
                            sql.Identifier(column["name"]),
                            sql.SQL(column["type"]),
                        )
                    )
            conn.commit()
        conn.close()

    def add_document(self, doc_id: str, chunks: dict[int, dict[str, Any]], supp_id: str = "", metadata: Optional[dict] = None) -> None:
        # Add the docs to the sqlite table
        conn = psycopg2.connect(
            dbname=self.database,
            user=self.username,
            password=self.password,
            host=self.host,
            port=self.port
        )
        cur = conn.cursor()
        # Create a created on timestamp
        created_on = str(int(time.time()))

        # Turn the metadata object into a string
        metadata = serialize_metadata(metadata)

        # Get the data from the dictionary
        for chunk_index, chunk in chunks.items():
            chunk_text = chunk.get("chunk_text", "")
            chunk_length = len(chunk_text)

            values_dict = {
                'doc_id': doc_id,
                'document_title': chunk.get("document_title", ""),
                'document_summary': chunk.get("document_summary", ""),
                'section_title': chunk.get("section_title", ""),
                'section_summary': chunk.get("section_summary", ""),
                'chunk_text': chunk.get("chunk_text", ""),
                'chunk_page_start': chunk.get("chunk_page_start", None),
                'chunk_page_end': chunk.get("chunk_page_end", None),
                'is_visual': chunk.get("is_visual", False),
                'chunk_index': chunk_index,
                'chunk_length': chunk_length,
                'created_on': created_on,
                'supp_id': supp_id,
                'metadata': metadata
            }

            # Generate the column names and placeholders
            columns = ', '.join(values_dict.keys())
            placeholders = ', '.join(['%s'] * len(values_dict))

            sql = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
            cur.execute(sql, tuple(values_dict.values()))

        conn.commit()
        conn.close()

    def remove_document(self, doc_id: str) -> None:
        # Remove the docs from the sqlite table
        conn = psycopg2.connect(
            dbname=self.database,
            user=self.username,
            password=self.password,
            host=self.host,
            port=self.port
        )
        cur = conn.cursor()
        from psycopg2 import sql
        cur.execute(
            sql.SQL("DELETE FROM {} WHERE doc_id = %s").format(sql.Identifier(self.table_name)),
            (doc_id,),
        )
        conn.commit()
        conn.close()

    def get_document(
        self, doc_id: str, include_content: bool = False
    ) -> Optional[FormattedDocument]:
        # Retrieve the document from the sqlite table
        conn = psycopg2.connect(
            dbname=self.database,
            user=self.username,
            password=self.password,
            host=self.host,
            port=self.port
        )
        cur = conn.cursor()
        columns = ["supp_id", "document_title", "document_summary", "created_on", "metadata"]
        if include_content:
            columns += ["chunk_text", "chunk_index"]

        from psycopg2 import sql
        query_statement = sql.SQL("SELECT {} FROM {} WHERE doc_id = %s").format(
            sql.SQL(", ").join([sql.Identifier(c) for c in columns]),
            sql.Identifier(self.table_name),
        )
        cur.execute(query_statement, (doc_id,))
        results = cur.fetchall()
        conn.close()

        # If there are no results, return None
        if not results:
            return None

        # Turn the results into an object where the columns are keys
        full_document_string = ""
        if include_content:
            # Concatenate the chunks into a single string
            for result in results:
                # Join each chunk text with a new line character
                full_document_string += result[columns.index("chunk_text")] + "\n"
            # Remove the last new line character
            full_document_string = full_document_string[:-1]

        supp_id = results[0][columns.index("supp_id")]
        title = results[0][columns.index("document_title")]
        summary = results[0][columns.index("document_summary")]
        created_on = results[0][columns.index("created_on")]
        metadata = results[0][columns.index("metadata")]

        # Convert the metadata string back into a dictionary
        metadata = deserialize_metadata(metadata)

        return FormattedDocument(
            id=doc_id,
            supp_id=supp_id,
            title=title,
            content=full_document_string if include_content else None,
            summary=summary,
            created_on=created_on,
            metadata=metadata
        )

    def get_chunk_text(self, doc_id: str, chunk_index: int) -> Optional[str]:
        # Retrieve the chunk text from the sqlite table
        conn = psycopg2.connect(
            dbname=self.database,
            user=self.username,
            password=self.password,
            host=self.host,
            port=self.port
        )
        cur = conn.cursor()
        from psycopg2 import sql
        cur.execute(
            sql.SQL("SELECT chunk_text FROM {} WHERE doc_id = %s AND chunk_index = %s").format(
                sql.Identifier(self.table_name)
            ),
            (doc_id, chunk_index),
        )
        result = cur.fetchone()
        conn.close()
        if result:
            return result[0]
        return None
    
    def get_is_visual(self, doc_id: str, chunk_index: int) -> Optional[bool]:
        # Retrieve the is_visual flag from the sqlite table
        conn = psycopg2.connect(
            dbname=self.database,
            user=self.username,
            password=self.password,
            host=self.host,
            port=self.port
        )
        cur = conn.cursor()
        from psycopg2 import sql
        cur.execute(
            sql.SQL("SELECT is_visual FROM {} WHERE doc_id = %s AND chunk_index = %s").format(
                sql.Identifier(self.table_name)
            ),
            (doc_id, chunk_index),
        )
        result = cur.fetchone()
        conn.close()
        if result:
            return result[0]
        return None
    
    def get_chunk_page_numbers(self, doc_id: str, chunk_index: int) -> Optional[tuple[int, int]]:
        # Retrieve the chunk page numbers from the sqlite table
        conn = psycopg2.connect(
            dbname=self.database,
            user=self.username,
            password=self.password,
            host=self.host,
            port=self.port
        )
        cur = conn.cursor()
        from psycopg2 import sql
        cur.execute(
            sql.SQL("SELECT chunk_page_start, chunk_page_end FROM {} WHERE doc_id = %s AND chunk_index = %s").format(
                sql.Identifier(self.table_name)
            ),
            (doc_id, chunk_index),
        )
        result = cur.fetchone()
        conn.close()
        if result:
            return result
        return None

    def get_document_title(self, doc_id: str, chunk_index: int) -> Optional[str]:
        # Retrieve the document title from the sqlite table
        conn = psycopg2.connect(
            dbname=self.database,
            user=self.username,
            password=self.password,
            host=self.host,
            port=self.port
        )
        cur = conn.cursor()
        from psycopg2 import sql
        cur.execute(
            sql.SQL("SELECT document_title FROM {} WHERE doc_id = %s AND chunk_index = %s").format(
                sql.Identifier(self.table_name)
            ),
            (doc_id, chunk_index),
        )
        result = cur.fetchone()
        conn.close()
        if result:
            return result[0]
        return None

    def get_document_summary(self, doc_id: str, chunk_index: int) -> Optional[str]:
        # Retrieve the document summary from the sqlite table
        conn = psycopg2.connect(
            dbname=self.database,
            user=self.username,
            password=self.password,
            host=self.host,
            port=self.port
        )
        cur = conn.cursor()
        from psycopg2 import sql
        cur.execute(
            sql.SQL("SELECT document_summary FROM {} WHERE doc_id = %s AND chunk_index = %s").format(
                sql.Identifier(self.table_name)
            ),
            (doc_id, chunk_index),
        )
        result = cur.fetchone()
        conn.close()
        if result:
            return result[0]
        return None

    def get_section_title(self, doc_id: str, chunk_index: int) -> Optional[str]:
        # Retrieve the section title from the sqlite table
        conn = psycopg2.connect(
            dbname=self.database,
            user=self.username,
            password=self.password,
            host=self.host,
            port=self.port
        )
        cur = conn.cursor()
        from psycopg2 import sql
        cur.execute(
            sql.SQL("SELECT section_title FROM {} WHERE doc_id = %s AND chunk_index = %s").format(
                sql.Identifier(self.table_name)
            ),
            (doc_id, chunk_index),
        )
        result = cur.fetchone()
        conn.close()
        if result:
            return result[0]
        return None

    def get_section_summary(self, doc_id: str, chunk_index: int) -> Optional[str]:
        # Retrieve the section summary from the sqlite table
        conn = psycopg2.connect(
            dbname=self.database,
            user=self.username,
            password=self.password,
            host=self.host,
            port=self.port
        )
        cur = conn.cursor()
        from psycopg2 import sql
        cur.execute(
            sql.SQL("SELECT section_summary FROM {} WHERE doc_id = %s AND chunk_index = %s").format(
                sql.Identifier(self.table_name)
            ),
            (doc_id, chunk_index),
        )
        result = cur.fetchone()
        conn.close()
        if result:
            return result[0]
        return None

    def get_all_doc_ids(self, supp_id: Optional[str] = None) -> list[str]:
        # Retrieve all document IDs from the sqlite table
        conn = psycopg2.connect(
            dbname=self.database,
            user=self.username,
            password=self.password,
            host=self.host,
            port=self.port
        )
        cur = conn.cursor()
        from psycopg2 import sql
        query_statement = sql.SQL("SELECT DISTINCT doc_id FROM {}").format(sql.Identifier(self.table_name))
        if supp_id:
            query_statement += sql.SQL(" WHERE supp_id = %s")
            cur.execute(query_statement, (supp_id,))
        else:
            cur.execute(query_statement)
        results = cur.fetchall()
        conn.close()
        return [result[0] for result in results]
    
    def get_document_count(self) -> int:
        # Retrieve the number of documents in the sqlite table
        conn = psycopg2.connect(
            dbname=self.database,
            user=self.username,
            password=self.password,
            host=self.host,
            port=self.port
        )
        cur = conn.cursor()
        cur.execute(f"SELECT COUNT(DISTINCT doc_id) FROM {self.table_name}")
        result = cur.fetchone()
        conn.close()
        if result is None:
            return 0
        return result[0]

    def get_total_num_characters(self) -> int:
        # Retrieve the total number of characters in the sqlite table
        conn = psycopg2.connect(
            dbname=self.database,
            user=self.username,
            password=self.password,
            host=self.host,
            port=self.port
        )
        cur = conn.cursor()
        cur.execute(f"SELECT SUM(chunk_length) FROM {self.table_name}")
        result = cur.fetchone()
        conn.close()
        if result is None or result[0] is None:
            return 0
        return result[0]

    def delete(self) -> None:
        # Delete the postgres table
        conn = psycopg2.connect(
            dbname=self.database,
            user=self.username,
            password=self.password,
            host=self.host,
            port=self.port
        )
        cur = conn.cursor()
        cur.execute(f"DROP TABLE {self.table_name}")
        conn.commit()
        conn.close()

    def to_dict(self) -> dict[str, str]:
        return {
            **super().to_dict(),
            "kb_id": self.kb_id,
            "username": self.username,
            "database": self.database,
            "host": self.host,
            "port": self.port,
        }
