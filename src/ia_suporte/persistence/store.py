from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from ia_suporte.agents.base import AgentContext, AgentResult


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ConversationStore:
    """Persists conversation state and message history in two SQLite databases."""

    def __init__(self, data_dir: Path | str | None = None) -> None:
        # se data_dir não é fornecido, cria o diretório "data" na raiz do projeto
        root = Path(data_dir) if data_dir else Path(__file__).resolve().parents[3] / "data"
        root.mkdir(parents=True, exist_ok=True)

        self.conversations_db = root / "conversations.db"
        self.messages_db = root / "messages.db"
        self._initialize()

    # funcao que faz a conexão com o banco de dados
    # contextmanager permite o uso do with
    @contextmanager
    def _connect(self, path: Path):
        connection = sqlite3.connect(path)
        connection.row_factory = sqlite3.Row
        try:
            # no yield o código do bloco with é executado, e depois o commit é feito
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    # inicializa o banco de dados, criando as tabelas se não existirem
    def _initialize(self) -> None:
        # cria a tabela de conversas
        with self._connect(self.conversations_db) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id UUID PRIMARY KEY,
                    client_id VARCHAR NOT NULL,
                    system VARCHAR NOT NULL DEFAULT '',
                    product VARCHAR NOT NULL DEFAULT '',
                    department VARCHAR NOT NULL DEFAULT '',
                    status VARCHAR NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_conversations_client_status "
                "ON conversations (client_id, status)"
            )
        # cria a tabela de mensagens
        with self._connect(self.messages_db) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    message_id UUID PRIMARY KEY,
                    conversation_id UUID NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    author VARCHAR NOT NULL,
                    text TEXT NOT NULL,
                    department VARCHAR NOT NULL DEFAULT ''
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_messages_conversation_timestamp "
                "ON messages (conversation_id, timestamp)"
            )

    # mudar pra nao criar o id
    def get_or_create_conversation(
        self,
        *,
        client_id: str,
        conversation_id: UUID | None = None,
    ) -> dict[str, Any]:
        if conversation_id is None:
            # depois melhorar implementacao de erros
            raise ValueError("conversation_id must be provided")

        conversation_id_text = str(conversation_id)

        # busca a conversa pelo id
        with self._connect(self.conversations_db) as connection:
            row = connection.execute(
                "SELECT * FROM conversations WHERE conversation_id = ?",
                (conversation_id_text,),
            ).fetchone()
        if row:
            return dict(row)

        # se nao achar, adiciona uma nova conversa com status IN_PROGRESS
        with self._connect(self.conversations_db) as connection:
            now = _now()
            
            connection.execute(
                """
                INSERT INTO conversations
                (conversation_id, client_id, status, created_at, updated_at)
                VALUES (?, ?, 'IN_PROGRESS', ?, ?)
                """,
                (conversation_id_text, client_id, now, now),
            )

            return {
                "conversation_id": conversation_id_text,
                "client_id": client_id,
                "system": "",
                "product": "",
                "department": "",
                "status": "IN_PROGRESS",
                "created_at": now,
                "updated_at": now,
            }

    # retorna o historico da conversa, ordenado por timestamp e rowid (para garantir a ordem correta)
    def get_history(self, conversation_id: UUID | str) -> list[str]:
        with self._connect(self.messages_db) as connection:
            rows = connection.execute(
                """
                SELECT author, text FROM messages
                WHERE conversation_id = ?
                ORDER BY timestamp, rowid
                """,
                (str(conversation_id),),
            ).fetchall()
        return [f"{row['author']}: {row['text']}" for row in rows]

    def reset_conversation(self, conversation_id: UUID | str) -> None:
        conversation_id_text = str(conversation_id)

        with self._connect(self.messages_db) as connection:
            connection.execute(
                "DELETE FROM messages WHERE conversation_id = ?",
                (conversation_id_text,),
            )

        with self._connect(self.conversations_db) as connection:
            connection.execute(
                "DELETE FROM conversations WHERE conversation_id = ?",
                (conversation_id_text,),
            )

    # adiciona uma mensagem ao historico da conversa
    def add_message(
        self,
        *,
        conversation_id: UUID | str,
        author: str,
        text: str,
        department: str,
        message_id: UUID | None = None,
        timestamp: str | None = None,
    ) -> UUID:
        generated_message_id = message_id or uuid4()
        with self._connect(self.messages_db) as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO messages
                (message_id, conversation_id, timestamp, author, text, department)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    str(generated_message_id),
                    str(conversation_id),
                    timestamp or _now(),
                    author,
                    text,
                    department,
                ),
            )
        return generated_message_id

    # atualiza os campos da conversa, se forem fornecidos
    def update_conversation(
        self,
        conversation_id: UUID | str,
        *,
        system: str | None = None,
        product: str | None = None,
        department: str | None = None,
        status: str | None = None,
    ) -> None:
        """Atualiza os campos da conversa, se forem fornecidos."""

        updates = {"updated_at": _now()}
        
        for key, value in {
            "system": system,
            "product": product,
            "department": department,
            "status": status,
        }.items():
            if value is not None:
                updates[key] = value

        assignments = ", ".join(f"{key} = ?" for key in updates)
        with self._connect(self.conversations_db) as connection:
            connection.execute(
                f"UPDATE conversations SET {assignments} WHERE conversation_id = ?",
                (*updates.values(), str(conversation_id)),
            )
    
    # constrói o contexto do agente com base na conversa
    def build_context(self, conversation: dict[str, Any]) -> AgentContext:
        conversation_id = conversation["conversation_id"]
        return AgentContext(
            conversation_id=conversation_id,
            client_id=conversation["client_id"],
            history=self.get_history(conversation_id),
            system=conversation["system"],
            product=conversation["product"],
            department=conversation["department"],
            status=conversation["status"],
        )

    # persiste o resultado da execução do agente (adiciona a resposta no historico e atualiza a conversa)
    def persist_result(self, context: AgentContext, result: AgentResult) -> None:
        metadata = result.metadata
        self.add_message(
            conversation_id=context.conversation_id,
            author=f"{result.department}_AGENT",
            text=result.response,
            department=result.department,
        )
        self.update_conversation(
            context.conversation_id,
            system=str(metadata.get("system", context.system)),
            product=str(metadata.get("product", context.product)),
            department=result.department,
            status=result.status,
        )
