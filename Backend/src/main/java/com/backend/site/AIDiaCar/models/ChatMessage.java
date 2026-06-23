package com.backend.site.AIDiaCar.models;

import com.backend.site.AIDiaCar.DiagnosticSession;
import jakarta.persistence.*;
import java.util.Date;

@Entity(name = "chat_messages")
@Table(name = "chat_messages")
public class ChatMessage {

    @Id
    @Column(name = "message_id")
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer messageId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "session_id", nullable = false)
    private DiagnosticSession session;

    @Column(name = "role", nullable = false, length = 10)
    private String role;  // "user" или "ai"

    @Column(name = "content", nullable = false, columnDefinition = "TEXT")
    private String content;

    @Column(name = "created_at", nullable = false)
    @Temporal(TemporalType.TIMESTAMP)
    private Date createdAt;

    @Column(name = "manual_references", columnDefinition = "TEXT")
    private String manualReferences;

    @Column(name = "image_url", length = 500)
    private String imageUrl;

    @Column(name = "page_number")
    private Integer pageNumber;

    @Column(name = "message_type", length = 20)
    private String messageType = "TEXT";

    public ChatMessage() {
        this.createdAt = new Date();
    }

    public ChatMessage(DiagnosticSession session, String role, String content) {
        this.session = session;
        this.role = role;
        this.content = content;
        this.createdAt = new Date();
        this.messageType = "TEXT";
    }

    public Integer getMessageId() {
        return messageId;
    }
    public void setMessageId(Integer messageId) {
        this.messageId = messageId;
    }

    public DiagnosticSession getSession() {
        return session;
    }
    public void setSession(DiagnosticSession session) {
        this.session = session;
    }

    public String getRole() {
        return role;
    }
    public void setRole(String role) {
        this.role = role;
    }

    public String getContent() {
        return content;
    }
    public void setContent(String content) {
        this.content = content;
    }

    public Date getCreatedAt() {
        return createdAt;
    }
    public void setCreatedAt(Date createdAt) {
        this.createdAt = createdAt;
    }

    public String getManualReferences() {
        return manualReferences;
    }
    public void setManualReferences(String manualReferences) {
        this.manualReferences = manualReferences;
    }

    public String getImageUrl() {
        return imageUrl;
    }
    public void setImageUrl(String imageUrl) {
        this.imageUrl = imageUrl;
    }

    public Integer getPageNumber() {
        return pageNumber;
    }
    public void setPageNumber(Integer pageNumber) {
        this.pageNumber = pageNumber;
    }

    public String getMessageType() {
        return messageType;
    }
    public void setMessageType(String messageType) {
        this.messageType = messageType;
    }
}