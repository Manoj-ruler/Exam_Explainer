    -- Exam Explainer Bot - Supabase Database Schema
    -- Run this SQL in Supabase SQL Editor

    -- Enable pgvector extension for embeddings
    CREATE EXTENSION IF NOT EXISTS vector;

    -- ============ DOCUMENTS TABLE (Vector Store) ============
    CREATE TABLE IF NOT EXISTS documents (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        content TEXT NOT NULL,
        embedding vector(768),  -- Gemini embedding dimension
        source TEXT,
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- Create index for vector similarity search
    CREATE INDEX IF NOT EXISTS documents_embedding_idx ON documents 
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

    -- ============ CHAT SESSIONS TABLE ============
    CREATE TABLE IF NOT EXISTS chat_sessions (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
        title TEXT DEFAULT 'New conversation',
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- ============ MESSAGES TABLE ============
    CREATE TABLE IF NOT EXISTS messages (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
        role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
        content TEXT NOT NULL,
        citations JSONB DEFAULT '[]',
        created_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- ============ USER PREFERENCES TABLE ============
    CREATE TABLE IF NOT EXISTS user_preferences (
        user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
        language TEXT DEFAULT 'English',
        created_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- ============ ROW LEVEL SECURITY ============

    -- Enable RLS on all tables
    ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
    ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
    ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
    ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

    -- Documents: Anyone can read (for now, since it's knowledge base)
    CREATE POLICY "Documents are publicly readable"
    ON documents FOR SELECT USING (true);

    -- Documents: Only authenticated users can insert (for admin)
    CREATE POLICY "Authenticated users can insert documents"
    ON documents FOR INSERT WITH CHECK (auth.role() = 'authenticated');

    -- Chat sessions: Users can only access their own
    CREATE POLICY "Users can manage their own sessions"
    ON chat_sessions FOR ALL USING (auth.uid() = user_id);

    -- Messages: Users can only access messages in their sessions
    CREATE POLICY "Users can manage messages in their sessions"
    ON messages FOR ALL USING (
        session_id IN (SELECT id FROM chat_sessions WHERE user_id = auth.uid())
    );

    -- User preferences: Users can only access their own
    CREATE POLICY "Users can manage their own preferences"
    ON user_preferences FOR ALL USING (auth.uid() = user_id);

    -- ============ VECTOR SEARCH FUNCTION ============
    CREATE OR REPLACE FUNCTION match_documents(
        query_embedding vector(768),
        match_count INT DEFAULT 5
    )
    RETURNS TABLE(id UUID, content TEXT, similarity FLOAT)
    LANGUAGE plpgsql
    AS $$
    BEGIN
        RETURN QUERY
        SELECT 
            documents.id,
            documents.content,
            1 - (documents.embedding <=> query_embedding) AS similarity
        FROM documents
        ORDER BY documents.embedding <=> query_embedding
        LIMIT match_count;
    END;
    $$;

    -- Grant execute permission
    GRANT EXECUTE ON FUNCTION match_documents TO authenticated;
    GRANT EXECUTE ON FUNCTION match_documents TO anon;
