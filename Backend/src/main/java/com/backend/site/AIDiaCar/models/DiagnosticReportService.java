package com.backend.site.AIDiaCar.models;

import com.backend.site.AIDiaCar.DiagnosticSession;
import com.backend.site.AIDiaCar.models.ChatMessage;
import com.backend.site.AIDiaCar.repository.ChatMessageRepository;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.PDPage;
import org.apache.pdfbox.pdmodel.PDPageContentStream;
import org.apache.pdfbox.pdmodel.common.PDRectangle;
import org.apache.pdfbox.pdmodel.font.PDType0Font;
import org.apache.pdfbox.pdmodel.font.PDType1Font;
import org.springframework.stereotype.Service;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.List;

@Service
public class DiagnosticReportService {

    private final ChatMessageRepository chatMessageRepository;

    public DiagnosticReportService(ChatMessageRepository chatMessageRepository) {
        this.chatMessageRepository = chatMessageRepository;
    }

    private String sanitizeText(String text) {
        if (text == null) return "";
        StringBuilder sb = new StringBuilder();
        for (char c : text.toCharArray()) {
            if ((c >= 'а' && c <= 'я') || (c >= 'А' && c <= 'Я') || c == 'ё' || c == 'Ё') {
                sb.append(c);
            }
            else if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z')) {
                sb.append(c);
            }
            else if (c >= '0' && c <= '9') {
                sb.append(c);
            }
            else if (c == ' ' || c == '.' || c == ',' || c == '!' || c == '?' ||
                    c == '-' || c == '_' || c == ':' || c == ';' || c == '(' || c == ')' ||
                    c == '[' || c == ']' || c == '{' || c == '}' || c == '/' || c == '\\' ||
                    c == '@' || c == '#' || c == '$' || c == '%' || c == '^' || c == '&' ||
                    c == '*' || c == '+' || c == '=' || c == '<' || c == '>' || c == '|' ||
                    c == '~' || c == '`' || c == '\'' || c == '"') {
                sb.append(c);
            }
            else if (c == '\n' || c == '\r' || c == '\t') {
                sb.append(' ');
            }
        }
        String result = sb.toString().replaceAll("\\s+", " ");
        return result.trim();
    }

    public byte[] generateReport(DiagnosticSession session) throws IOException {
        List<ChatMessage> messages = chatMessageRepository.findBySession_SessionIDOrderByCreatedAtAsc(session.getSessionID());

        try (PDDocument document = new PDDocument()) {
            PDPage page = new PDPage(PDRectangle.A4);
            document.addPage(page);

            PDType0Font regularFont = null;
            PDType0Font boldFont = null;
            try {
                regularFont = PDType0Font.load(document, getClass().getResourceAsStream("/fonts/LiberationSans-Regular.ttf"));
            } catch (Exception e) {
                System.err.println("Не загружен LiberationSans-Regular.ttf: " + e.getMessage());
            }
            try {
                boldFont = PDType0Font.load(document, getClass().getResourceAsStream("/fonts/LiberationSans-Bold.ttf"));
            } catch (Exception e) {
                System.err.println("Не загружен LiberationSans-Bold.ttf: " + e.getMessage());
            }

            PDPageContentStream contentStream = new PDPageContentStream(document, page);
            contentStream.beginText();
            contentStream.newLineAtOffset(50, 750);

            if (boldFont != null) contentStream.setFont(boldFont, 16);
            else contentStream.setFont(PDType1Font.HELVETICA_BOLD, 16);
            contentStream.showText(sanitizeText("ДИАГНОСТИЧЕСКАЯ КАРТА"));
            contentStream.newLineAtOffset(0, -25);

            if (regularFont != null) contentStream.setFont(regularFont, 10);
            else contentStream.setFont(PDType1Font.HELVETICA, 10);
            SimpleDateFormat sdf = new SimpleDateFormat("dd.MM.yyyy HH:mm");
            contentStream.showText(sanitizeText("Сессия #" + session.getSessionID()));
            contentStream.newLineAtOffset(0, -15);
            contentStream.showText(sanitizeText("Дата создания: " + sdf.format(session.getCreatedAt())));
            contentStream.newLineAtOffset(0, -15);
            contentStream.showText(sanitizeText("Статус: " + session.getStatus()));
            if (session.getCompletedAt() != null) {
                contentStream.showText(sanitizeText(" (завершена " + sdf.format(session.getCompletedAt()) + ")"));
            }
            contentStream.newLineAtOffset(0, -25);

            if (boldFont != null) contentStream.setFont(boldFont, 12);
            else contentStream.setFont(PDType1Font.HELVETICA_BOLD, 12);
            contentStream.showText(sanitizeText("Автомобиль:"));
            contentStream.newLineAtOffset(0, -20);
            if (regularFont != null) contentStream.setFont(regularFont, 10);
            else contentStream.setFont(PDType1Font.HELVETICA, 10);
            String carInfo = (session.getCar().getBrand() != null ? session.getCar().getBrand() : "")
                    + " " + (session.getCar().getModel() != null ? session.getCar().getModel() : "")
                    + " (" + (session.getCar().getYear() != null ? session.getCar().getYear() : "?") + ")";
            contentStream.showText(sanitizeText(carInfo));
            contentStream.newLineAtOffset(0, -15);
            if (session.getCar().getTypeEngine() != null && !session.getCar().getTypeEngine().isEmpty()) {
                contentStream.showText(sanitizeText("Двигатель: " + session.getCar().getTypeEngine()));
                contentStream.newLineAtOffset(0, -15);
            }
            if (session.getCar().getGeneration() != null && !session.getCar().getGeneration().isEmpty()) {
                contentStream.showText(sanitizeText("Поколение: " + session.getCar().getGeneration()));
                contentStream.newLineAtOffset(0, -15);
            }
            contentStream.newLineAtOffset(0, -25);

            if (boldFont != null) contentStream.setFont(boldFont, 12);
            else contentStream.setFont(PDType1Font.HELVETICA_BOLD, 12);
            contentStream.showText(sanitizeText("Ход диагностики:"));
            contentStream.newLineAtOffset(0, -20);
            if (regularFont != null) contentStream.setFont(regularFont, 10);
            else contentStream.setFont(PDType1Font.HELVETICA, 10);

            int lineCount = 0;
            int maxLinesPerPage = 45;
            for (ChatMessage msg : messages) {
                String role = "user".equals(msg.getRole()) ? "Владелец" : "AI Диагност";
                String fullLine = sanitizeText(role + ": " + msg.getContent());
                int maxChars = 90;
                int start = 0;
                while (start < fullLine.length()) {
                    int end = Math.min(start + maxChars, fullLine.length());
                    String part = fullLine.substring(start, end);
                    if (start == 0) {
                        contentStream.showText(part);
                    } else {
                        contentStream.showText("   " + part);
                    }
                    contentStream.newLineAtOffset(0, -15);
                    start = end;
                    lineCount++;
                    if (lineCount >= maxLinesPerPage) {
                        contentStream.endText();
                        contentStream.close();
                        page = new PDPage(PDRectangle.A4);
                        document.addPage(page);
                        contentStream = new PDPageContentStream(document, page);
                        contentStream.beginText();
                        contentStream.newLineAtOffset(50, 750);
                        if (regularFont != null) contentStream.setFont(regularFont, 10);
                        else contentStream.setFont(PDType1Font.HELVETICA, 10);
                        lineCount = 0;
                    }
                }
                contentStream.newLineAtOffset(0, -5);
                lineCount++;
                if (lineCount >= maxLinesPerPage) {
                    contentStream.endText();
                    contentStream.close();
                    page = new PDPage(PDRectangle.A4);
                    document.addPage(page);
                    contentStream = new PDPageContentStream(document, page);
                    contentStream.beginText();
                    contentStream.newLineAtOffset(50, 750);
                    if (regularFont != null) contentStream.setFont(regularFont, 10);
                    else contentStream.setFont(PDType1Font.HELVETICA, 10);
                    lineCount = 0;
                }
            }

            contentStream.endText();
            contentStream.close();

            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            document.save(baos);
            return baos.toByteArray();
        }
    }
}