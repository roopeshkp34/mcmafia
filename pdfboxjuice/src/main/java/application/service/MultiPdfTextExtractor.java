package application.service;

import org.apache.pdfbox.io.MemoryUsageSetting;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.PDPage;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class MultiPdfTextExtractor {

    public Map<String, Object> extractTextFromFiles(List<MultipartFile> files, Boolean computeImages) throws IOException {
        Map<String, Object> result = new HashMap<>();

        for (MultipartFile file : files) {
            Map<String, Object> fileData = new HashMap<>();
            
            try (PDDocument document = PDDocument.load(file.getInputStream(), MemoryUsageSetting.setupMainMemoryOnly())) {
                // Extract Text
                DetailedTextStripper stripper = new DetailedTextStripper();
                stripper.setSortByPosition(true);
                stripper.getText(document);
                
                Map<String, Object> textData = new HashMap<>();
                textData.put("pageCount", document.getNumberOfPages());
                textData.put("pages", stripper.getPages());
                fileData.put("text", textData);

                // Extract Images if requested
                Map<String, Object> imagesData = new HashMap<>();
                if (Boolean.TRUE.equals(computeImages)) {
                    int pageNum = 1;
                    for (PDPage page : document.getPages()) {
                        ImageLocationExtractor imageExtractor = new ImageLocationExtractor(page);
                        imageExtractor.processPage(page);
                        imagesData.put(String.valueOf(pageNum), imageExtractor.getImages());
                        pageNum++;
                    }
                }
                fileData.put("images", imagesData);
            }
            result.put(file.getOriginalFilename(), fileData);
        }
        return result;
    }
}
