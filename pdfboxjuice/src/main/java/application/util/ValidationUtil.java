package application.util;

import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;

public class ValidationUtil {

    public static void validatePdfFiles(List<MultipartFile> files) throws IOException {
        if (files == null || files.isEmpty()) {
            throw new IllegalArgumentException("No files provided");
        }

        for (MultipartFile file : files) {
            if (file.isEmpty()) {
                throw new IllegalArgumentException("One or more files are empty");
            }
            if (!"application/pdf".equals(file.getContentType())) {
                throw new IllegalArgumentException("One or more files are not PDFs: " + file.getOriginalFilename());
            }
        }
    }
}
