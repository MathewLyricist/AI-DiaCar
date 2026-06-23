package com.backend.site.AIDiaCar.pdfParse;

import net.sourceforge.tess4j.Tesseract;
import net.sourceforge.tess4j.TesseractException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import javax.imageio.ImageIO;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.rendering.PDFRenderer;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;

@Service
public class OcrService {

    private final Tesseract tesseract;

    @Value("${tesseract.datapath:src/main/resources/tessdata}")
    private String tessDataPath;

    public OcrService() {
        tesseract = new Tesseract();
        tesseract.setLanguage("rus+eng");
        tesseract.setPageSegMode(1);
    }

    public String extractTextFromPdf(File pdfFile) throws IOException, TesseractException {
        StringBuilder fullText = new StringBuilder();

        try (PDDocument document = PDDocument.load(pdfFile)) {
            PDFRenderer pdfRenderer = new PDFRenderer(document);
            int totalPages = document.getNumberOfPages();

            for (int page = 0; page < totalPages; page++) {
                BufferedImage image = pdfRenderer.renderImageWithDPI(page, 300);
                String pageText = tesseract.doOCR(image);
                fullText.append("=== СТРАНИЦА ").append(page + 1).append(" ===\n");
                fullText.append(pageText).append("\n\n");
            }
        }

        return fullText.toString();
    }

    public String extractTextFromImage(BufferedImage image) throws TesseractException {
        return tesseract.doOCR(image);
    }

    public String extractTextFromImageFile(File imageFile) throws IOException, TesseractException {
        BufferedImage image = ImageIO.read(imageFile);
        return tesseract.doOCR(image);
    }
}