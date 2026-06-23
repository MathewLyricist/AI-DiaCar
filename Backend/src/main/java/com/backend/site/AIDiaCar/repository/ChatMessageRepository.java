package com.backend.site.AIDiaCar.repository;

import com.backend.site.AIDiaCar.models.ChatMessage;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface ChatMessageRepository extends JpaRepository<ChatMessage, Integer> {

    List<ChatMessage> findBySession_SessionIDOrderByCreatedAtAsc(Integer sessionId);

    @Query("SELECT m FROM chat_messages m WHERE m.session.sessionID = :sessionId " +
            "ORDER BY m.createdAt DESC")
    List<ChatMessage> findTop50BySession_SessionIDOrderByCreatedAtDesc(@Param("sessionId") Integer sessionId);

    List<ChatMessage> findBySession_SessionIDAndRoleOrderByCreatedAtAsc(Integer sessionId, String role);

    void deleteBySession_SessionID(Integer sessionId);

    long countBySession_SessionID(Integer sessionId);

    List<ChatMessage> findBySession_SessionIDAndMessageTypeOrderByCreatedAtAsc(Integer sessionId, String messageType);
}