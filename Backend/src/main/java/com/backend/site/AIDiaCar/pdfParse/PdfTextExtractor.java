package com.backend.site.AIDiaCar.pdfParse;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.IOException;

@Service
public class PdfTextExtractor {

    private final PdfTypeDetector pdfTypeDetector;
    private final OcrService ocrService;

    public PdfTextExtractor(PdfTypeDetector pdfTypeDetector, OcrService ocrService) {
        this.pdfTypeDetector = pdfTypeDetector;
        this.ocrService = ocrService;
    }

    public String extractText(File pdfFile) throws IOException {
        PdfTypeDetector.PdfType pdfType = pdfTypeDetector.detectPdfType(pdfFile);

        System.out.println("Тип PDF: " + pdfType);

        switch (pdfType) {
            case TEXT:
                return extractTextFromTextPdf(pdfFile);
            case SCANNED:
                return extractTextWithOcr(pdfFile);
            case HYBRID:
                return extractTextFromHybridPdf(pdfFile);
            default:
                throw new IOException("Неизвестный тип PDF");
        }
    }

    private String extractTextFromTextPdf(File pdfFile) throws IOException {
        try (PDDocument document = PDDocument.load(pdfFile)) {
            PDFTextStripper stripper = new PDFTextStripper();
            stripper.setSortByPosition(true);
            return stripper.getText(document);
        }
    }

    private String extractTextWithOcr(File pdfFile) throws IOException {
        try {
            return ocrService.extractTextFromPdf(pdfFile);
        } catch (Exception e) {
            throw new IOException("Ошибка OCR: " + e.getMessage(), e);
        }
    }

    private String extractTextFromHybridPdf(File pdfFile) throws IOException {
        StringBuilder fullText = new StringBuilder();

        try (PDDocument document = PDDocument.load(pdfFile)) {
            PDFTextStripper textStripper = new PDFTextStripper();
            org.apache.pdfbox.rendering.PDFRenderer pdfRenderer =
                    new org.apache.pdfbox.rendering.PDFRenderer(document);
            int totalPages = document.getNumberOfPages();

            for (int i = 1; i <= totalPages; i++) {
                textStripper.setStartPage(i);
                textStripper.setEndPage(i);
                String pageText = textStripper.getText(document);

                if (pageText == null || pageText.trim().length() < 50) {
                    System.out.println("Страница " + i + " - используем OCR");
                    try {
                        var image = pdfRenderer.renderImageWithDPI(i - 1, 300);
                        String ocrText = ocrService.extractTextFromImage(image);
                        fullText.append("=== СТРАНИЦА ").append(i).append(" (OCR) ===\n");
                        fullText.append(ocrText).append("\n\n");
                    } catch (Exception e) {
                        fullText.append("=== СТРАНИЦА ").append(i).append(" (ошибка OCR) ===\n\n");
                    }
                } else {
                    fullText.append("=== СТРАНИЦА ").append(i).append(" (TEXT) ===\n");
                    fullText.append(pageText).append("\n\n");
                }
            }
        }

        return fullText.toString();
    }

    public String cleanText(String text) {
        if (text == null) return "";
        text = text.replaceAll("\\s+", " ");
        text = text.replaceAll("[^\\w\\s.,;:!?()\\-]", " ");
        text = text.replaceAll(" {2,}", " ");
        return text.trim();
    }
}