package application.service;

import org.apache.pdfbox.cos.COSName;
import org.apache.pdfbox.pdmodel.PDPage;
import org.apache.pdfbox.pdmodel.graphics.image.PDImage;
import org.apache.pdfbox.pdmodel.graphics.state.PDGraphicsState;
import org.apache.pdfbox.util.Matrix;
import org.apache.pdfbox.contentstream.PDFGraphicsStreamEngine;

import java.awt.geom.Point2D;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class ImageLocationExtractor extends PDFGraphicsStreamEngine {
    private final List<Map<String, Object>> images = new ArrayList<>();
    private final int pageHeight;

    public ImageLocationExtractor(PDPage page) {
        super(page);
        this.pageHeight = (int) page.getCropBox().getHeight();
    }

    public List<Map<String, Object>> getImages() {
        return images;
    }

    @Override
    public void drawImage(PDImage pdImage) throws IOException {
        Matrix ctm = getGraphicsState().getCurrentTransformationMatrix();
        
        float x = ctm.getTranslateX();
        float y = ctm.getTranslateY();
        float w = ctm.getScaleX();
        float h = ctm.getScaleY();

        float top = pageHeight - (y + h);
        float bottom = pageHeight - y;

        Map<String, Object> imageInfo = new HashMap<>();
        imageInfo.put("x0", x);
        imageInfo.put("x1", x + w);
        imageInfo.put("top", top);
        imageInfo.put("bottom", bottom);
        imageInfo.put("width", w);
        imageInfo.put("height", h);
        imageInfo.put("raw_width", pdImage.getWidth());
        imageInfo.put("raw_height", pdImage.getHeight());
        imageInfo.put("name", "Image");

        images.add(imageInfo);
    }

    @Override
    public void appendRectangle(Point2D p0, Point2D p1, Point2D p2, Point2D p3) throws IOException {}

    @Override
    public void clip(int windingRule) throws IOException {}

    @Override
    public void moveTo(float x, float y) throws IOException {}

    @Override
    public void lineTo(float x, float y) throws IOException {}

    @Override
    public void curveTo(float x1, float y1, float x2, float y2, float x3, float y3) throws IOException {}

    @Override
    public Point2D getCurrentPoint() throws IOException { return new Point2D.Float(0, 0); }

    @Override
    public void closePath() throws IOException {}

    @Override
    public void endPath() throws IOException {}

    @Override
    public void strokePath() throws IOException {}

    @Override
    public void fillPath(int windingRule) throws IOException {}

    @Override
    public void shadingFill(COSName shadingName) throws IOException {}

    @Override
    public void fillAndStrokePath(int windingRule) throws IOException {}
}
