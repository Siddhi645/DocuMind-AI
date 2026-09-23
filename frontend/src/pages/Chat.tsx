/**
 * DocuMind AI — AI Chat Page
 * The primary RAG interface for asking questions about institutional documents.
 */

import React, { useState, useRef, useEffect } from 'react';
import { api, type ChatResponse, type SourceCitation } from '../services/api';
import './Chat.css';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: SourceCitation[];
  timestamp: Date;
}

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>();
  const [department, setDepartment] = useState('');
  const [academicYear, setAcademicYear] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSend = async () => {
    const trimmed = question.trim();
    if (!trimmed || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: trimmed,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setQuestion('');
    setIsLoading(true);

    try {
      const response = await api.chat({
        question: trimmed,
        session_id: sessionId,
        filters: {
          department: department || undefined,
          academic_year: academicYear || undefined,
        },
      });

      const data: ChatResponse = response.data;
      if (!sessionId && data.session_id) {
        setSessionId(data.session_id);
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content:
          err?.response?.status === 501
            ? '[Phase 1] The RAG pipeline is a stub. Connect Pinecone + LLM in Phase 2 to get real answers.'
            : 'An error occurred while processing your question. Please try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const clearChat = () => {
    setMessages([]);
    setSessionId(undefined);
  };

  return (
    <div className="chat-page">
      {/* Header */}
      <div className="chat-header page-header">
        <div>
          <h1 className="page-title">AI Chat</h1>
          <p className="page-subtitle">Ask questions about institutional documents</p>
        </div>
        {messages.length > 0 && (
          <button className="btn btn-ghost btn-sm" onClick={clearChat} id="chat-clear-btn">
            New conversation
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="chat-filters card">
        <span className="chat-filters-label">Filters (optional)</span>
        <select
          className="input chat-filter-select"
          value={department}
          onChange={(e) => setDepartment(e.target.value)}
          id="chat-dept-filter"
        >
          <option value="">All departments</option>
          <option value="CSE">Computer Science & Engineering</option>
          <option value="ECE">Electronics & Communication</option>
          <option value="MECH">Mechanical Engineering</option>
          <option value="CIVIL">Civil Engineering</option>
          <option value="Admin">Administration</option>
        </select>
        <select
          className="input chat-filter-select"
          value={academicYear}
          onChange={(e) => setAcademicYear(e.target.value)}
          id="chat-year-filter"
        >
          <option value="">All years</option>
          <option value="2025-26">2025–26</option>
          <option value="2024-25">2024–25</option>
          <option value="2023-24">2023–24</option>
        </select>
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-empty">
            <div className="chat-empty-icon">◎</div>
            <h3>Ask DocuMind AI</h3>
            <p>Ask any question about institutional documents, NAAC/NBA criteria, policies, or reports.</p>
            <div className="chat-suggestions">
              {[
                'What evidence exists for student mentoring activities?',
                'What faculty development programs were conducted?',
                'What are the examination regulations?',
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  className="chat-suggestion"
                  onClick={() => setQuestion(suggestion)}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`chat-message chat-message-${msg.role}`}>
            <div className="chat-bubble">
              <p className="chat-bubble-text">{msg.content}</p>

              {/* Source citations */}
              {msg.role === 'assistant' && msg.sources && msg.sources.length > 0 && (
                <div className="chat-sources">
                  <h4 className="chat-sources-title">Sources</h4>
                  {msg.sources.map((source, idx) => (
                    <div key={idx} className="chat-source">
                      <div className="chat-source-header">
                        <span className="chat-source-icon">📄</span>
                        <span className="chat-source-name">{source.document_name}</span>
                        {source.page && (
                          <span className="badge badge-info">Page {source.page}</span>
                        )}
                        {source.score && (
                          <span className="chat-source-score">
                            {(source.score * 100).toFixed(0)}% match
                          </span>
                        )}
                      </div>
                      {source.section && (
                        <p className="chat-source-section">§ {source.section}</p>
                      )}
                      {source.snippet && (
                        <blockquote className="chat-source-snippet">{source.snippet}</blockquote>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
            <span className="chat-time">
              {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          </div>
        ))}

        {isLoading && (
          <div className="chat-message chat-message-assistant">
            <div className="chat-bubble chat-bubble-loading">
              <span className="chat-typing-dot" />
              <span className="chat-typing-dot" />
              <span className="chat-typing-dot" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="chat-input-area">
        <textarea
          id="chat-input"
          className="chat-input"
          placeholder="Ask about institutional documents, NAAC/NBA criteria, policies…"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          rows={1}
        />
        <button
          id="chat-send-btn"
          className="btn btn-primary chat-send-btn"
          onClick={handleSend}
          disabled={isLoading || !question.trim()}
          title="Send (Enter)"
        >
          {isLoading ? <span className="spinner spinner-sm" /> : '→'}
        </button>
      </div>
    </div>
  );
};

export default ChatPage;
