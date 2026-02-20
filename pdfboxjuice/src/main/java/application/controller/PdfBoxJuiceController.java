package application.controller;

import application.service.MultiPdfTextExtractor;
import application.util.ValidationUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
public class PdfBoxJuiceController {
    private final Logger LOGGER = LoggerFactory.getLogger(PdfBoxJuiceController.class);

    @Autowired
    private MultiPdfTextExtractor extractor;

    @PostMapping("/bulk/extract-text-info")
    public ResponseEntity<Map<String, Object>> getTextInfo(
            @RequestPart(value = "input-pdf") List<MultipartFile> pdf_files,
            @RequestParam(value = "compute-images", required = false, defaultValue = "false") Boolean compute_images
    ) {
        try {
            ValidationUtil.validatePdfFiles(pdf_files);

            LOGGER.info("Parsing Started For Extraction");
            Map<String, Object> textDetails = extractor.extractTextFromFiles(pdf_files, compute_images);
            Map<String, Object> responseMap = new HashMap<>();
            responseMap.put("result", textDetails);

            LOGGER.info("Parsing Ended For Extraction");
            return ResponseEntity.status(HttpStatus.OK).body(responseMap);
        } catch (IllegalArgumentException e) {
            LOGGER.error("Validation Error: ", e);
            HashMap<String, Object> errorMap = new HashMap<>();
            errorMap.put("error", e.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(errorMap);
        } catch (IOException e) {
            LOGGER.error("Processing Error: ", e);
            HashMap<String, Object> errorMap = new HashMap<>();
            errorMap.put("error", "Error processing PDF files");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorMap);
        }
    }
}
