package com.backend.site.AIDiaCar.pdfParse;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.IOException;

@Service
public class PdfTypeDetector {

    public enum PdfType {
        TEXT,
        SCANNED,
        HYBRID
    }

    public PdfType detectPdfType(File pdfFile) throws IOException {
        try (PDDocument document = PDDocument.load(pdfFile)) {
            PDFTextStripper stripper = new PDFTextStripper();
            int totalPages = document.getNumberOfPages();
            int textPages = 0;

            for (int i = 1; i <= totalPages; i++) {
                stripper.setStartPage(i);
                stripper.setEndPage(i);
                String pageText = stripper.getText(document);

                if (pageText != null && pageText.trim().length() > 50) {
                    textPages++;
                }
            }

            if (textPages == 0) {
                return PdfType.SCANNED;
            } else if (textPages == totalPages) {
                return PdfType.TEXT;
            } else {
                return PdfType.HYBRID;
            }
        }
    }

    public boolean hasTextLayer(File pdfFile) throws IOException {
        try (PDDocument document = PDDocument.load(pdfFile)) {
            PDFTextStripper stripper = new PDFTextStripper();
            String text = stripper.getText(document);
            return text != null && text.trim().length() > 100;
        }
    }
}