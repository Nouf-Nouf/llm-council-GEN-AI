import { useState, useEffect } from 'react';
import { useTheme } from '../ThemeContext.jsx';
import './Sidebar.css';

export default function Sidebar({
  conversations,
  currentConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
}) {
  const { theme, toggleTheme } = useTheme();

  const handleDeleteConversation = async (e, conversationId) => {
    e.stopPropagation(); // Prevent triggering the conversation selection
    try {
      await onDeleteConversation(conversationId);
    } catch (error) {
      console.error('Failed to delete conversation:', error);
      alert('Failed to delete conversation. Please try again.');
    }
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-title-row">
          <div className="brand">
            <div className="brand-text">
              <h1>LLM Council</h1>
            </div>
          </div>
          <button className="theme-toggle-btn" onClick={toggleTheme}>
            {theme === 'light' ? 'Dark' : 'Light'}
          </button>
        </div>
        <div className="header-buttons">
          <button className="new-conversation-btn" onClick={onNewConversation}>
            <span className="btn-icon">+</span>
            New Conversation
          </button>
        </div>
      </div>

      <div className="conversation-section">
        <div className="section-head">
          <div className="section-title">Conversations</div>
          <div className="section-count">{conversations.length}</div>
        </div>
        <div className="conversation-list">
          {conversations.length === 0 ? (
            <div className="no-conversations">
              <div className="empty-title">No conversations yet</div>
              <div className="empty-subtitle">Start a new conversation to begin exploring AI insights</div>
            </div>
          ) : (
            conversations.map((conv) => (
              <div
                key={conv.id}
                className={`conversation-item ${
                  conv.id === currentConversationId ? 'active' : ''
                }`}
                onClick={() => onSelectConversation(conv.id)}
              >
                <div className="conversation-title-row">
                  <div className="conversation-title">
                    {conv.title || 'New Conversation'}
                  </div>
                  <div className="conversation-actions">
                    <button
                      className="delete-conv-btn"
                      onClick={(e) => handleDeleteConversation(e, conv.id)}
                      title="Delete conversation"
                    >
                      ×
                    </button>
                  </div>
                </div>
                <div className="conversation-meta">
                  {conv.message_count} messages
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
