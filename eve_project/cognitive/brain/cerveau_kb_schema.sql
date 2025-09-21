-- cerveau_kb_schema.sql
-- Schéma de la base de données KnowledgeBase pour ALMA Cerveau V20.5

CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filepath TEXT UNIQUE NOT NULL,
    checksum TEXT NOT NULL,
    last_processed_utc TEXT NOT NULL,
    size_bytes INTEGER,
    encoding TEXT,
    embedding BLOB -- Clé : Ajouté pour le stockage des embeddings de documents
);

CREATE TABLE IF NOT EXISTS linguistic_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    token_text TEXT,
    lemma TEXT,
    pos TEXT,
    is_stop BOOLEAN,
    is_punct BOOLEAN,
    is_alpha BOOLEAN,
    is_significant BOOLEAN,
    FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_linguistic_tokens_file_id ON linguistic_tokens (file_id);
CREATE INDEX IF NOT EXISTS idx_linguistic_tokens_lemma ON linguistic_tokens (lemma);

CREATE TABLE IF NOT EXISTS named_entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    entity_text TEXT,
    entity_type TEXT,
    start_char INTEGER,
    end_char INTEGER,
    FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_named_entities_file_id ON named_entities (file_id);
CREATE INDEX IF NOT EXISTS idx_named_entities_text_type ON named_entities (entity_text, entity_type);

CREATE TABLE IF NOT EXISTS metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    meta_key TEXT NOT NULL,
    meta_value TEXT,
    FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_metadata_file_id ON metadata (file_id);

CREATE TABLE IF NOT EXISTS entity_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    source_entity_id INTEGER,
    target_entity_id INTEGER,
    relation_type TEXT,
    context_snippet TEXT,
    FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE,
    FOREIGN KEY (source_entity_id) REFERENCES named_entities (id) ON DELETE SET NULL,
    FOREIGN KEY (target_entity_id) REFERENCES named_entities (id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_entity_relations_file_id ON entity_relations (file_id);
