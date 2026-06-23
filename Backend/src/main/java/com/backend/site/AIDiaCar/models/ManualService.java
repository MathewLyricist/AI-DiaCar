package com.backend.site.AIDiaCar.models;

import com.backend.site.AIDiaCar.repository.ManualRepository;
import com.backend.site.AIDiaCar.pdfParse.PdfTextExtractor;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;
import org.springframework.beans.factory.annotation.Value;
import com.backend.site.AIDiaCar.models.Manual;
import org.springframework.stereotype.Service;
import jakarta.annotation.PostConstruct;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

@Service
public class ManualService {
    private final ManualRepository manualRepository;
    private final PdfTextExtractor pdfTextExtractor;

    @Value("${manuals.root.path:../AIModel/DataPDF}")
    private String rootPath;

    public ManualService(ManualRepository manualRepository, PdfTextExtractor pdfTextExtractor) {
        this.manualRepository = manualRepository;
        this.pdfTextExtractor = pdfTextExtractor;
    }

    @PostConstruct
    public void init() {
        try {
            Files.createDirectories(Paths.get(rootPath));
            System.out.println("Директория для мануалов: " + Paths.get(rootPath).toAbsolutePath());
        } catch (IOException e) {
            throw new RuntimeException("Не удалось создать директорию для мануалов: " + e.getMessage(), e);
        }
    }

    private String fixBrokenWords(String text) {
        if (text == null || text.isEmpty()) return text;
        text = text.replaceAll("(?i)www\\.box\\-m\\.info", "");
        text = text.replaceAll("([а-яА-Яa-zA-Z]+)-\\s+([а-яА-Яa-zA-Z]+)", "$1$2");
        text = text.replaceAll("([а-яА-Яa-zA-Z]+)-\\s*\\n\\s*([а-яА-Яa-zA-Z]+)", "$1$2");
        text = text.replaceAll("\\b([а-яА-Я])\\s+([а-яА-Я])\\s+([а-яА-Я])\\s*", "$1$2$3");
        text = text.replaceAll("\\b([а-яА-Я])\\s+([а-яА-Я])\\s*", "$1$2");
        text = text.replaceAll("[ \\t]{2,}", " ");
        return text;
    }

    public String extractFullTextFromManual(String pdfPath, String model) {
        if (pdfPath == null || pdfPath.isEmpty()) {
            System.err.println("⚠️ Путь к мануалу пустой");
            return "";
        }

        try {
            File file = new File(pdfPath);
            if (!file.isAbsolute()) {
                file = file.getCanonicalFile();
            }

            System.out.println("📖 [ManualService] Извлечение полного текста...");
            System.out.println("📖 [ManualService] Путь: " + file.getAbsolutePath());

            if (file.isDirectory()) {
                File[] pdfFiles = file.listFiles((d, name) -> name.toLowerCase().endsWith(".pdf"));
                if (pdfFiles == null || pdfFiles.length == 0) {
                    return "";
                }

                if (model != null && !model.isEmpty()) {
                    for (File pdfFile : pdfFiles) {
                        if (pdfFile.getName().toLowerCase().contains(model.toLowerCase())) {
                            file = pdfFile;
                            break;
                        }
                    }
                }
                if (file.isDirectory()) {
                    file = pdfFiles[0];
                }
            }

            if (!file.exists() || !file.isFile()) {
                return "";
            }

            StringBuilder fullText = new StringBuilder();
            try (PDDocument document = PDDocument.load(file)) {
                PDFTextStripper stripper = new PDFTextStripper();
                stripper.setSortByPosition(true);
                stripper.setLineSeparator("\n");

                int totalPages = document.getNumberOfPages();
                for (int page = 1; page <= totalPages; page++) {
                    stripper.setStartPage(page);
                    stripper.setEndPage(page);
                    String pageText = stripper.getText(document);
                    fullText.append("\n=== СТРАНИЦА ").append(page).append(" ===\n");
                    fullText.append(pageText).append("\n");
                }
            }

            String extractedText = fullText.toString();
            System.out.println("✅ [ManualService] Извлечено исходных символов: " + extractedText.length());

            String fixed = fixBrokenWords(extractedText);
            String cleaned = cleanupExtractedText(fixed);
            System.out.println("✅ [ManualService] После очистки: " + cleaned.length() + " символов");

            try {
                java.nio.file.Files.write(
                        java.nio.file.Paths.get("manual_text_debug.txt"),
                        cleaned.getBytes()
                );
                System.out.println("📄 Очищенный текст сохранён в manual_text_debug.txt");
            } catch (IOException e) {
                System.err.println("⚠️ Не удалось сохранить текст: " + e.getMessage());
            }

            if (cleaned.length() > 0) {
                System.out.println("📄 [DEBUG] Первые 500 символов после очистки:\n" +
                        cleaned.substring(0, Math.min(500, cleaned.length())));
            } else {
                System.out.println("📄 [DEBUG] Очищенный текст пуст");
            }

            TextQuality quality = assessTextQuality(cleaned);
            System.out.println("🔍 [ManualService] Качество очищенного текста: " + quality);

            if (quality == TextQuality.VERY_POOR || cleaned.trim().isEmpty()) {
                System.out.println("⚠️ [ManualService] Качество очень низкое, пробуем альтернативный метод...");
                String alternativeText = extractTextAlternative(file);
                if (alternativeText != null && !alternativeText.isEmpty()) {
                    String altCleaned = fixBrokenWords(alternativeText);
                    altCleaned = cleanupExtractedText(altCleaned);
                    System.out.println("✅ [ManualService] Используем альтернативный текст (длина " + altCleaned.length() + ")");
                    return altCleaned;
                }
            }

            if (cleaned.trim().isEmpty()) {
                System.out.println("⚠️ [ManualService] Очищенный текст пуст, возвращаем неочищенный (сырой) текст");
                String rawText = extractedText.replaceAll("(?m)^=== СТРАНИЦА \\d+ ===\\s*", "");
                rawText = rawText.replaceAll("\\s+", " ");
                return rawText;
            }

            return cleaned;

        } catch (IOException e) {
            System.err.println("❌ Ошибка: " + e.getMessage());
            return "";
        }
    }

    private TextQuality assessTextQuality(String text) {
        if (text == null || text.isEmpty()) {
            return TextQuality.EMPTY;
        }

        int totalLines = text.split("\n").length;
        if (totalLines == 0) return TextQuality.EMPTY;

        int shortLines = 0;
        int fragmentedLines = 0;
        int mixedContentLines = 0;

        String[] lines = text.split("\n");
        for (String line : lines) {
            line = line.trim();
            if (line.isEmpty()) continue;

            if (line.length() < 20) {
                shortLines++;
            }

            if (Pattern.compile("[а-яА-Яa-zA-Z]-\\s*$").matcher(line).find()) {
                fragmentedLines++;
            }

            if (line.contains(" - ") && line.split(" - ").length > 2) {
                mixedContentLines++;
            }
        }

        double shortRatio = (double) shortLines / totalLines;
        double fragmentedRatio = (double) fragmentedLines / totalLines;
        double mixedRatio = (double) mixedContentLines / totalLines;

        System.out.println("📊 [Quality] Коротких строк: " + String.format("%.1f", shortRatio * 100) + "%");
        System.out.println("📊 [Quality] Разорванных: " + String.format("%.1f", fragmentedRatio * 100) + "%");
        System.out.println("📊 [Quality] Смешанных: " + String.format("%.1f", mixedRatio * 100) + "%");

        if (shortRatio > 0.4 || fragmentedRatio > 0.3 || mixedRatio > 0.3) {
            return TextQuality.VERY_POOR;
        } else if (shortRatio > 0.25 || fragmentedRatio > 0.2 || mixedRatio > 0.2) {
            return TextQuality.POOR;
        } else if (shortRatio > 0.1 || fragmentedRatio > 0.1) {
            return TextQuality.ACCEPTABLE;
        } else {
            return TextQuality.GOOD;
        }
    }

    private String extractTextAlternative(File file) {
        try (PDDocument document = PDDocument.load(file)) {
            StringBuilder fullText = new StringBuilder();

            PDFTextStripper stripper = new PDFTextStripper();
            stripper.setSortByPosition(false);
            stripper.setLineSeparator("\n");

            int totalPages = document.getNumberOfPages();
            for (int page = 1; page <= totalPages; page++) {
                stripper.setStartPage(page);
                stripper.setEndPage(page);
                String pageText = stripper.getText(document);
                pageText = cleanupExtractedText(pageText);
                fullText.append("\n=== СТРАНИЦА ").append(page).append(" ===\n");
                fullText.append(pageText).append("\n");
            }

            return fullText.toString();
        } catch (IOException e) {
            System.err.println("❌ [Alternative] Ошибка: " + e.getMessage());
            return "";
        }
    }

    private String removeTocLines(String text) {
        text = text.replaceAll("(?m)^.*\\.\\.\\.\\s*\\d+.*$", "");
        text = text.replaceAll("(?m)^[\\d\\s\\.]+$", "");
        text = text.replaceAll("(?m)^РАЗДЕЛ\\s+\\d+.*$", "");
        text = text.replaceAll("(?m)^=== СТРАНИЦА \\d+ ===", "");
        return text;
    }

    private String mergeBrokenLines(String text) {
        text = text.replaceAll("([а-яА-Яa-zA-Z]+)-\\s*\\n\\s*([а-яА-Яa-zA-Z]+)", "$1$2");
        text = text.replaceAll("([а-яА-Яa-z]+)\\s*[-–]\\s*\\n\\s*([а-яА-Яa-z]+)", "$1$2");
        text = text.replaceAll("\\b([а-яА-Яa-z])\\s+([а-яА-Яa-z]+)\\b", "$1$2");
        return text;
    }

    private String cleanupExtractedText(String text) {
        text = text.replaceAll("(?m)^=== СТРАНИЦА \\d+ ===\\s*", "");
        text = text.replaceAll("(?m)^[\\s]*\\.{3,}\\s*\\d+\\s*$", "");
        text = text.replaceAll("(?m)^[\\d\\s]+$", "");
        text = text.replaceAll("(?m)^РАЗДЕЛ\\s+\\d+.*$", "");
        text = text.replaceAll("(?i)\\b(рис\\.\\s*\\d+[-\\d]*)\\b", "");
        text = text.replaceAll("([а-яА-Яa-zA-Z]+)-\\s*\\n\\s*([а-яА-Яa-zA-Z]+)", "$1$2");
        text = text.replaceAll("\\n{3,}", "\n\n");
        return text.trim();
    }

    public String extractTextFromManual(String pdfPath, String model) {
        if (pdfPath == null || pdfPath.isEmpty()) {
            System.err.println("⚠️ Путь к мануалу пустой");
            return "";
        }

        try {
            File file = new File(pdfPath);
            if (!file.isAbsolute()) {
                file = file.getCanonicalFile();
            }

            System.out.println("📖 [ManualService] Исходный путь: " + pdfPath);
            System.out.println("📖 [ManualService] Абсолютный путь: " + file.getAbsolutePath());
            System.out.println("📖 [ManualService] Существует: " + file.exists());
            System.out.println("📖 [ManualService] Это директория: " + file.isDirectory());

            if (file.isDirectory()) {
                System.out.println("📂 [ManualService] Это директория, ищем PDF файлы...");

                File[] pdfFiles = file.listFiles((dir, name) -> name.toLowerCase().endsWith(".pdf"));
                if (pdfFiles == null || pdfFiles.length == 0) {
                    System.err.println("❌ PDF файлы не найдены в директории: " + file.getAbsolutePath());
                    return "";
                }

                System.out.println("✅ [ManualService] Найдено PDF файлов: " + pdfFiles.length);
                for (File f : pdfFiles) {
                    System.out.println("   - " + f.getName());
                }

                if (model != null && !model.isEmpty()) {
                    System.out.println("🔍 [ManualService] Поиск по модели: " + model);
                    for (File pdfFile : pdfFiles) {
                        String fileName = pdfFile.getName().toLowerCase();
                        System.out.println("   🔍 Проверяем: " + fileName + " содержит " + model.toLowerCase() + "? " + fileName.contains(model.toLowerCase()));
                        if (fileName.contains(model.toLowerCase())) {
                            file = pdfFile;
                            System.out.println("✅ [ManualService] Найден по модели: " + file.getName());
                            break;
                        }
                    }
                }

                if (file.isDirectory()) {
                    file = pdfFiles[0];
                    System.out.println("✅ [ManualService] Берём первый: " + file.getName());
                }
            }

            if (!file.exists()) {
                System.err.println("❌ Файл не найден: " + file.getAbsolutePath());
                System.err.println("💡 Текущий каталог: " + System.getProperty("user.dir"));
                return "";
            }

            if (!file.isFile()) {
                System.err.println("❌ Это не файл: " + file.getAbsolutePath());
                return "";
            }

            StringBuilder text = new StringBuilder();
            try (PDDocument document = PDDocument.load(file)) {
                PDFTextStripper stripper = new PDFTextStripper();
                stripper.setSortByPosition(true);
                text.append(stripper.getText(document));
            }

            System.out.println("✅ [ManualService] Извлечено символов: " + text.length());
            return text.toString().trim();

        } catch (IOException e) {
            System.err.println("❌ Ошибка: " + e.getMessage());
            e.printStackTrace();
            return "";
        }
    }

    public String extractTextFromManual(String pdfPath) {
        return extractTextFromManual(pdfPath, null);
    }

    public byte[] convertPageToImage(String pdfPath, int pageNumber) {
        try {
            File file = new File(pdfPath);
            if (!file.isAbsolute()) {
                file = file.getCanonicalFile();
            }

            if (file.isDirectory()) {
                File[] pdfFiles = file.listFiles((d, name) -> name.toLowerCase().endsWith(".pdf"));
                if (pdfFiles != null && pdfFiles.length > 0) {
                    file = pdfFiles[0];
                }
            }

            if (!file.exists() || !file.isFile()) {
                System.err.println("❌ Файл не найден: " + file.getAbsolutePath());
                return null;
            }

            try (PDDocument document = PDDocument.load(file)) {
                if (pageNumber < 1 || pageNumber > document.getNumberOfPages()) {
                    System.err.println("❌ Страница " + pageNumber + " не существует (всего: " + document.getNumberOfPages() + ")");
                    return null;
                }

                org.apache.pdfbox.rendering.PDFRenderer pdfRenderer = new org.apache.pdfbox.rendering.PDFRenderer(document);
                java.awt.image.BufferedImage image = pdfRenderer.renderImageWithDPI(pageNumber, 150);

                java.io.ByteArrayOutputStream baos = new java.io.ByteArrayOutputStream();
                javax.imageio.ImageIO.write(image, "PNG", baos);

                System.out.println("✅ [ManualService] Конвертирована страница " + pageNumber + " в изображение");
                return baos.toByteArray();
            }

        } catch (IOException e) {
            System.err.println("❌ [ManualService] Ошибка конвертации страницы в изображение: " + e.getMessage());
            e.printStackTrace();
            return null;
        }
    }

    public boolean hasManualForCar(String brand, String model) {
        return findManualForCar(brand, model).isPresent();
    }

    public List<com.backend.site.AIDiaCar.models.Manual> findAll() {
        return new ArrayList<>(manualRepository.findAll());
    }

    public void scanAndRegisterManuals() throws IOException {
        File rootDir = new File(rootPath);
        if (!rootDir.exists()) {
            System.out.println("Директория " + rootPath + " не найдена. Создаем...");
            Files.createDirectories(Paths.get(rootPath));
            return;
        }

        File[] brandDirs = rootDir.listFiles(File::isDirectory);
        if (brandDirs == null) return;

        for (File brandDir : brandDirs) {
            String brandName = brandDir.getName();
            System.out.println("Сканирование бренда: " + brandName);

            File commonDir = new File(brandDir, "Common");
            if (commonDir.exists()) {
                registerManual(brandName, null, commonDir.getPath(), "BRAND_COMMON");
            }

            File[] modelDirs = brandDir.listFiles(File::isDirectory);
            if (modelDirs != null) {
                for (File modelDir : modelDirs) {
                    if (!modelDir.getName().equals("Common")) {
                        registerManual(brandName, modelDir.getName(), modelDir.getPath(), "SPECIFIC");
                    }
                }
            }
        }

        File generalCommonDir = new File(rootPath, "Common");
        if (generalCommonDir.exists()) {
            registerManual("Common", null, generalCommonDir.getPath(), "GENERAL");
        }
    }

    private void registerManual(String brand, String model, String dirPath, String manualType) {
        if (model != null) {
            List<com.backend.site.AIDiaCar.models.Manual> existing = manualRepository.findByBrandAndModel(brand, model);
            if (!existing.isEmpty()) {
                System.out.println("  Мануал уже зарегистрирован: " + brand + " " + model + " (" + existing.size() + " записей)");
                return;
            }
        }

        File dir = new File(dirPath);
        File[] manualFiles = dir.listFiles((d, name) -> name.toLowerCase().endsWith(".pdf") || name.toLowerCase().endsWith(".djvu"));
        if (manualFiles != null && manualFiles.length > 0) {
            com.backend.site.AIDiaCar.models.Manual manual = new com.backend.site.AIDiaCar.models.Manual(brand, model, dirPath);
            manual.setFilePath(manualFiles[0].getPath());
            manual.setManualType(manualType);

            try {
                String text = pdfTextExtractor.extractText(manualFiles[0]);
                manual.setProcessedText(pdfTextExtractor.cleanText(text));
                manual.setProcessedAt(new java.util.Date());
                System.out.println("  Обработано: " + manualFiles[0].getName() + " (" + text.length() + " символов)");
            } catch (Exception e) {
                System.err.println("  Ошибка обработки: " + e.getMessage());
            }

            manualRepository.save(manual);
            System.out.println("  Зарегистрирован: " + brand + (model != null ? " " + model : " ") + " [" + manualType + "]");
        } else {
            System.out.println("  Нет файлов PDF/DJVU в: " + dirPath);
        }
    }

    public Optional<Manual> findManualForCar(String brand, String model) {
        List<Manual> manuals = manualRepository.findByBrandAndModelOrderedIgnoreCase(brand, model);
        if (!manuals.isEmpty()) {
            System.out.println("✅ Найден SPECIFIC мануал для " + brand + " " + model + ": " + manuals.get(0).getDirectoryPath());
            return Optional.of(manuals.get(0));
        }

        List<Manual> all = manualRepository.findAll();
        for (Manual m : all) {
            if (m.getBrand().equalsIgnoreCase(brand) && "BRAND_COMMON".equals(m.getManualType())) {
                System.out.println("✅ Найден BRAND_COMMON мануал для бренда " + brand);
                return Optional.of(m);
            }
        }

        List<Manual> general = manualRepository.findByManualType("GENERAL");
        if (!general.isEmpty()) {
            System.out.println("✅ Найден GENERAL мануал");
            return Optional.of(general.get(0));
        }

        System.out.println("❌ Мануал не найден для: " + brand + " " + model);
        return Optional.empty();
    }

    public List<String> getAvailableBrands() {
        return manualRepository.findAll().stream()
                .map(com.backend.site.AIDiaCar.models.Manual::getBrand)
                .filter(brand -> !brand.equals("Common"))
                .distinct()
                .sorted()
                .collect(Collectors.toList());
    }

    public List<String> getModelsForBrand(String brand) {
        return manualRepository.findByBrand(brand).stream()
                .map(com.backend.site.AIDiaCar.models.Manual::getModel)
                .filter(model -> model != null && !model.isEmpty())
                .distinct()
                .sorted()
                .collect(Collectors.toList());
    }

    private enum TextQuality {
        EMPTY, VERY_POOR, POOR, ACCEPTABLE, GOOD
    }

    public String findBestPdfForCar(String brand, String model, int year, String basePath) {
        File baseDir = new File(basePath);
        if (!baseDir.exists() || !baseDir.isDirectory()) return null;

        File modelDir = null;
        for (File f : baseDir.listFiles(File::isDirectory)) {
            if (f.getName().equalsIgnoreCase(model)) {
                modelDir = f;
                break;
            }
        }
        File searchDir = (modelDir != null) ? modelDir : baseDir;

        File[] pdfs = searchDir.listFiles((d, name) -> name.toLowerCase().endsWith(".pdf"));
        if (pdfs == null || pdfs.length == 0) return null;

        String modelNormalized = model.toLowerCase().replaceAll("[^a-z0-9]", "");
        List<File> goodMatches = new ArrayList<>();

        for (File pdf : pdfs) {
            String name = pdf.getName().toLowerCase();
            String baseName = name.replaceAll("_m\\d+", "").replaceAll("_p\\d+", "");
            baseName = baseName.replaceAll("_\\d{4}([-_]\\d{4})?", "").replace(".pdf", "");
            baseName = baseName.replaceAll("[^a-z0-9]", "");
            if (baseName.contains(modelNormalized) || modelNormalized.contains(baseName)) {
                goodMatches.add(pdf);
            }
        }

        if (goodMatches.isEmpty()) goodMatches.addAll(Arrays.asList(pdfs));

        File bestMatch = null;
        Pattern yearPattern = Pattern.compile("(\\d{4})[-_–]?(\\d{4})?");
        for (File pdf : goodMatches) {
            String name = pdf.getName();
            Matcher m = yearPattern.matcher(name);
            if (m.find()) {
                int start = Integer.parseInt(m.group(1));
                if (m.group(2) != null) {
                    int end = Integer.parseInt(m.group(2));
                    if (year >= start && year <= end) {
                        bestMatch = pdf;
                        break;
                    }
                } else {
                    if (start == year) {
                        bestMatch = pdf;
                        break;
                    }
                }
            } else if (bestMatch == null) {
                bestMatch = pdf;
            }
        }

        if (bestMatch == null && !goodMatches.isEmpty()) bestMatch = goodMatches.get(0);
        if (bestMatch != null) {
            System.out.println("✅ Найден PDF: " + bestMatch.getAbsolutePath());
            return bestMatch.getAbsolutePath();
        }
        return null;
    }

    public int getPageOffsetFromFileName(String pdfPath) {
        if (pdfPath == null) return 0;
        File file = new File(pdfPath);
        String name = file.getName().toLowerCase();

        Pattern pPattern = Pattern.compile("_p(\\d+)\\.pdf$", Pattern.CASE_INSENSITIVE);
        Matcher pMatcher = pPattern.matcher(name);
        if (pMatcher.find()) {
            return Integer.parseInt(pMatcher.group(1));
        }

        Pattern mPattern = Pattern.compile("_m(\\d+)\\.pdf$", Pattern.CASE_INSENSITIVE);
        Matcher mMatcher = mPattern.matcher(name);
        if (mMatcher.find()) {
            return -Integer.parseInt(mMatcher.group(1));
        }

        return 0;
    }

    private String getCachedText(File pdfFile) {
        File txtFile = new File(pdfFile.getParent(), pdfFile.getName().replace(".pdf", ".txt"));
        if (txtFile.exists()) {
            try {
                return new String(Files.readAllBytes(txtFile.toPath()), StandardCharsets.UTF_8);
            } catch (IOException e) {
            }
        }
        return null;
    }

    private void cacheText(File pdfFile, String text) {
        File txtFile = new File(pdfFile.getParent(), pdfFile.getName().replace(".pdf", ".txt"));
        try {
            Files.write(txtFile.toPath(), text.getBytes(StandardCharsets.UTF_8));
        } catch (IOException e) {
            System.err.println("Не удалось сохранить кэш: " + e.getMessage());
        }
    }
}