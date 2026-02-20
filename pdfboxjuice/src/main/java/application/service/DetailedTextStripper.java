package application.service;

import org.apache.pdfbox.text.PDFTextStripper;
import org.apache.pdfbox.text.TextPosition;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class DetailedTextStripper extends PDFTextStripper {
    private final Map<Integer, PageData> pages = new HashMap<>();

    public DetailedTextStripper() throws IOException {
    }

    public static class CharInfo {
        public String text;
        public float x0, x1, top, bottom, width, height, fontsize, rotation;
        public int page_number;
        public float widthOfSpace;
        public String fontname, fontType, fontSubType;
    }

    public static class LineInfo {
        public String text;
        public int page;
        public List<CharInfo> chars = new ArrayList<>();
    }

    public static class PageData {
        public List<Object> annotation = new ArrayList<>();
        public List<LineInfo> lineInfo = new ArrayList<>();
    }

    @Override
    protected void startPage(org.apache.pdfbox.pdmodel.PDPage page) throws IOException {
        super.startPage(page);
        int pageNum = getCurrentPageNo();
        pages.put(pageNum, new PageData());
    }

    @Override
    protected void writeString(String text, List<TextPosition> textPositions) throws IOException {
        int pageNum = getCurrentPageNo();
        PageData pageData = pages.get(pageNum);
        List<LineInfo> lineInfoList = pageData.lineInfo;

        LineInfo line = new LineInfo();
        line.text = text;
        line.page = pageNum;

        for (TextPosition textPosition : textPositions) {
            CharInfo charInfo = new CharInfo();
            charInfo.text = textPosition.getUnicode();
            charInfo.x0 = textPosition.getXDirAdj();
            charInfo.x1 = textPosition.getXDirAdj() + textPosition.getWidthDirAdj();
            charInfo.top = textPosition.getYDirAdj();
            charInfo.bottom = textPosition.getYDirAdj() + textPosition.getHeightDir();
            charInfo.width = textPosition.getWidthDirAdj();
            charInfo.height = textPosition.getHeightDir();
            charInfo.fontsize = textPosition.getFontSizeInPt();
            
            // Intern strings to save memory
            charInfo.fontname = textPosition.getFont().getName().intern();
            charInfo.rotation = textPosition.getDir();
            charInfo.page_number = pageNum;
            charInfo.widthOfSpace = textPosition.getWidthOfSpace();
            charInfo.fontType = "Font";
            charInfo.fontSubType = textPosition.getFont().getSubType().intern();

            line.chars.add(charInfo);
        }
        lineInfoList.add(line);
    }

    public Map<Integer, PageData> getPages() {
        return pages;
    }
}
